# patch_ve_kernel_exec.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Get-Location
$kernelPath = Join-Path $root "ve_kernel.ps1"

if (-not (Test-Path -LiteralPath $kernelPath)) {
  Write-Host "ve_kernel.ps1 not found in $root" -ForegroundColor Red
  exit 1
}

$src = Get-Content $kernelPath -Raw

# We will replace the whole Invoke-Exec function with the envelope-aware version.
$pattern = '(?s)function\s+Invoke-Exec\s*\{.*?\}'
$replacement = @'
function Invoke-Exec {
  param(
    [string[]]$CmdParts,
    [switch]$Envelope
  )

  if (-not $CmdParts -or $CmdParts.Count -eq 0) {
    Write-Host "VE kernel: empty exec command"
    Write-Ledger "fail" "exec" "empty exec command"
    exit 1
  }

  # strip internal marker if present
  $CmdParts = $CmdParts | Where-Object { $_ -ne "--ve:envelope" }

  $cmd = $CmdParts -join " "
  $output = ""
  $rc = 0

  try {
    $output = Invoke-Expression $cmd 2>&1
  } catch {
    $output = $_.Exception.Message
    $rc = 1
  }

  if ($rc -ne 0) {
    $output | Write-Output
    Write-Ledger "fail" "exec" ("rc={0}; out={1}" -f $rc, $output)
    if ($Envelope) {
      $payload = @{ rc = $rc; out = $output } | ConvertTo-Json -Compress
      $envJson = New-VECrossTalkEnvelope -PayloadJson $payload
      $envJson | Write-Output
    }
    exit $rc
  } else {
    if ($Envelope) {
      $payload = @{ rc = 0; out = $output } | ConvertTo-Json -Compress
      $envJson = New-VECrossTalkEnvelope -PayloadJson $payload
      $envJson | Write-Output
    } else {
      $output | Write-Output
    }
    Write-Ledger "ok" "exec" ("rc=0; out={0}" -f $output)
    exit 0
  }
}
'@

if ($src -notmatch $pattern) {
  Write-Host "Could not find existing Invoke-Exec in ve_kernel.ps1 — aborting." -ForegroundColor Red
  exit 1
}

$patched = [System.Text.RegularExpressions.Regex]::Replace($src, $pattern, $replacement)

$patched | Set-Content -LiteralPath $kernelPath -Encoding UTF8

Write-Host "ve_kernel.ps1 patched with envelope-aware Invoke-Exec." -ForegroundColor Green
