# ve_kernel.ps1 — VE execution wrapper (quotes/spaces safe via -EncodedCommand)

# Auto-import VE.Guard if available (non-fatal if missing)
try {
  $guard = Join-Path $PSScriptRoot "Modules\VE.Guard\VE.Guard.psd1"
  if (Test-Path $guard) { Import-Module $guard -Force | Out-Null }
} catch {}

function Invoke-Child {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)][string]$Command,
    [string]$ShellPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe",
    [switch]$PwshCore,
    [string]$WorkingDirectory,
    [int]$TimeoutSec = 15,
    [switch]$NoGuard,
    [string]$StdOutPath,
    [string]$StdErrPath
  )

  # Guard only when the command looks like a write/bypass attempt
  $needsGuard = $Command -match '(?i)\b(Set-Content|Add-Content|Out-File)\b|(?<!\S)(?:\d?>|>>)|\s--%\s'
  if (-not $NoGuard -and $needsGuard) {
    if (-not (Get-Command Assert-VeSafeWrite -ErrorAction SilentlyContinue)) {
      throw "Invoke-Child: VE Guard not loaded. Import VE.Guard or pass -NoGuard (not recommended)."
    }
    Assert-VeSafeWrite $Command
  }

  if ($PwshCore) { $ShellPath = "pwsh.exe" }
  $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
  $argLine = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand $encoded"

  $psi = @{ FilePath=$ShellPath; ArgumentList=$argLine; PassThru=$true; WindowStyle='Hidden' }
  if ($WorkingDirectory) { $psi.WorkingDirectory = $WorkingDirectory }
  if ($StdOutPath)       { $psi.RedirectStandardOutput = $StdOutPath }
  if ($StdErrPath)       { $psi.RedirectStandardError  = $StdErrPath }

  $p = Start-Process @psi
  if ($TimeoutSec -gt 0) {
    if (-not $p.WaitForExit($TimeoutSec * 1000)) { try { $p.Kill() } catch {}; throw "Invoke-Child: timed out after $TimeoutSec s" }
  } else {
    $p.WaitForExit()
  }
  return $p.ExitCode
}

function Invoke-ChildAsync {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)][string]$Command,
    [switch]$PwshCore,
    [switch]$NoGuard
  )
  $needsGuard = $Command -match '(?i)\b(Set-Content|Add-Content|Out-File)\b|(?<!\S)(?:\d?>|>>)|\s--%\s'
  if (-not $NoGuard -and $needsGuard) {
    if (-not (Get-Command Assert-VeSafeWrite -ErrorAction SilentlyContinue)) {
      throw "Invoke-ChildAsync: VE Guard not loaded."
    }
    Assert-VeSafeWrite $Command
  }
  $shell = if ($PwshCore) { 'pwsh.exe' } else { "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" }
  $enc   = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
  Start-Process -FilePath $shell -ArgumentList "-NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand $enc" -PassThru -WindowStyle Hidden
}

function Enter-VE { Set-Location $PSScriptRoot; "VE root: $((Get-Location).Path)" }