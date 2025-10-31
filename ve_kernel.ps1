param(
  [Parameter(Position=0)]
  [string]$Mode = "",
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Rest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RootDir        = Split-Path -Parent $MyInvocation.MyCommand.Path
$Ledger         = Join-Path $RootDir "ve_ledger.jsonl"
$PolicyFile     = Join-Path $RootDir "policies\ve_policy.json"
$CheckpointDir  = Join-Path $RootDir "checkpoints"
$SecretsDir     = Join-Path $RootDir "secrets"
$SharedKeyFile  = Join-Path $SecretsDir "ve_shared.key"

function Get-PolicyHash {
  if (Test-Path -LiteralPath $PolicyFile) {
    $bytes = [System.IO.File]::ReadAllBytes($PolicyFile)
    $sha   = [System.Security.Cryptography.SHA256]::Create()
    $hash  = $sha.ComputeHash($bytes)
    return -join ($hash | ForEach-Object { $_.ToString("x2") })
  } else {
    return "no-policy"
  }
}

function Get-VESecret {
  if (Test-Path -LiteralPath $SharedKeyFile) {
    return (Get-Content $SharedKeyFile -Raw -Encoding ascii)
  } else {
    return ""
  }
}

function New-VEHmac {
  param(
    [string]$Data,
    [string]$Key
  )
  if (-not $Key) { return "" }
  $hmac = New-Object System.Security.Cryptography.HMACSHA256
  $hmac.Key = [Text.Encoding]::UTF8.GetBytes($Key)
  $hashBytes = $hmac.ComputeHash([Text.Encoding]::UTF8.GetBytes($Data))
  return -join ($hashBytes | ForEach-Object { $_.ToString("x2") })
}

function New-VECrossTalkEnvelope {
  param(
    [string]$PayloadJson
  )
  $ts     = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  $ph     = Get-PolicyHash
  $nonce  = [guid]::NewGuid().ToString()
  $secret = Get-VESecret

  $env = [ordered]@{
    ver         = 1
    ts          = $ts
    policy_hash = $ph
    nonce       = $nonce
    payload     = $PayloadJson
  }

  $body = ($env | ConvertTo-Json -Compress)
  $sig  = New-VEHmac -Data $body -Key $secret
  $env.sig = $sig

  return ($env | ConvertTo-Json -Compress)
}

function Write-Ledger {
  param(
    [string]$Status,
    [string]$Action,
    [string]$Message
  )
  $ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  $ph = Get-PolicyHash
  $obj = [ordered]@{
    ts          = $ts
    status      = $Status
    action      = $Action
    policy_hash = $ph
    msg         = $Message
  }
  $json = $obj | ConvertTo-Json -Compress
  Add-Content -LiteralPath $Ledger -Value $json
}

function Invoke-Audit {
  $qc = Join-Path $RootDir "QUICKCHECK_LOGS"
  if (Test-Path -LiteralPath $qc) {
    Write-Host "[AUDIT] OK"
    Write-Ledger "ok" "audit" "QUICKCHECK_LOGS present"
    exit 0
  } else {
    Write-Host "[AUDIT] missing QUICKCHECK_LOGS"
    Write-Ledger "fail" "audit" "QUICKCHECK_LOGS missing"
    exit 20
  }
}

function Invoke-Revert {
  param([int]$Seq)
  $cp = Join-Path $CheckpointDir ("cp_{0}.json" -f $Seq)
  if (-not (Test-Path -LiteralPath $cp)) {
    Write-Host "[REVERT] no checkpoint"
    Write-Ledger "fail" "revert" "no checkpoint for seq=$Seq"
    exit 1
  }
  try {
    $json = Get-Content $cp -Raw | ConvertFrom-Json
  } catch {
    Write-Host "[REVERT] checkpoint corrupt: $cp"
    Write-Ledger "abort" "revert" "corrupt checkpoint: $cp"
    exit 30
  }
  $script:psi_eff = [double]$json.psi_eff
  Write-Host "[REVERT] restored seq=$Seq ψ_eff=$script:psi_eff"
  Write-Ledger "ok" "revert" "restored seq=$Seq ψ_eff=$script:psi_eff"
  exit 0
}

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

  $CmdParts = $CmdParts | Where-Object { $_ -ne "--ve:envelope" }

  $cmd    = $CmdParts -join " "
  $output = ""
  $rc     = 0

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
  }
  else {
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

switch ($Mode) {
  "audit" {
    Invoke-Audit
  }
  "revert" {
    $seq = if ($Rest.Count -gt 0) { [int]$Rest[0] } else { 0 }
    Invoke-Revert -Seq $seq
  }
  "policy-hash" {
    Get-PolicyHash
  }
  "exec" {
    $useEnv = $false
    if ($Rest.Count -gt 0 -and $Rest[0] -eq "-Envelope") {
      $useEnv = $true
      if ($Rest.Count -gt 1) {
        $Rest = $Rest[1..($Rest.Count - 1)]
      } else {
        $Rest = @()
      }
    }
    Invoke-Exec -CmdParts $Rest -Envelope:$useEnv
  }
  default {
    Write-Host "Vulpine Echo (Windows) kernel — clean"
    Write-Host "  .\ve_kernel.ps1 exec <cmd...>"
    Write-Host "  .\ve_kernel.ps1 exec -Envelope <cmd...>"
    Write-Host "  .\ve_kernel.ps1 audit"
    Write-Host "  .\ve_kernel.ps1 revert <seq>"
    Write-Host "  .\ve_kernel.ps1 policy-hash"
  }
}
