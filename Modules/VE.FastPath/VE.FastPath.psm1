function Start-VEWorker {
  param([switch]$PwshCore)
  if ($script:VE_Worker -and -not $script:VE_Worker.HasExited) { return $script:VE_Worker }

  $loop = @"
[Console]::InputEncoding  = [Text.Encoding]::UTF8
[Console]::OutputEncoding = [Text.Encoding]::UTF8
while (($line = [Console]::In.ReadLine()) -ne $null) {
  try {
    \$cmd = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String(\$line))
    \$Error.Clear(); \$global:LASTEXITCODE = 0
    Invoke-Expression \$cmd | Out-Null
    \$exit = if (\$Error.Count -gt 0) { 1 } else { if (\$LASTEXITCODE) { \$LASTEXITCODE } else { 0 } }
    [Console]::Out.WriteLine(\$exit)
  } catch {
    [Console]::Out.WriteLine(1)
  }
}
"@

  $workerPath = Join-Path $env:TEMP 've_worker_loop.ps1'
  Set-Content -Path $workerPath -Value $loop -Encoding UTF8

  $shell = if ($PwshCore) { 'pwsh.exe' } else { "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" }
  $si = New-Object System.Diagnostics.ProcessStartInfo
  $si.FileName  = $shell
  $si.Arguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$workerPath`""
  $si.UseShellExecute        = $false
  $si.RedirectStandardInput  = $true
  $si.RedirectStandardOutput = $true
  $si.RedirectStandardError  = $true
  $si.CreateNoWindow         = $true

  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $si
  [void]$p.Start()
  $script:VE_Worker = $p
  return $p
}

function Stop-VEWorker {
  if ($script:VE_Worker -and -not $script:VE_Worker.HasExited) { try { $script:VE_Worker.Kill() } catch {} }
  $script:VE_Worker = $null
}

function Invoke-ChildFast {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)][string]$Command,
    [switch]$NoGuard,
    [switch]$PwshCore,
    [int]$TimeoutSec = 10
  )

  # Guard for writes/redirection (expects VE.Guard)
  $needsGuard = $Command -match '(?i)\b(Set-Content|Add-Content|Out-File)\b|(?<!\S)(?:\d?>|>>)|\s--%\s'
  if (-not $NoGuard -and $needsGuard) {
    if (-not (Get-Command Assert-VeSafeWrite -ErrorAction SilentlyContinue)) {
      throw "Invoke-ChildFast: VE Guard not loaded."
    }
    Assert-VeSafeWrite $Command
  }

  $p   = Start-VEWorker -PwshCore:$PwshCore
  $b64 = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
  $p.StandardInput.WriteLine($b64)
  $p.StandardInput.Flush()

  # Non-blocking wait with timeout; surface stderr if stuck
  $sw = [Diagnostics.Stopwatch]::StartNew()
  while ($p.StandardOutput.Peek() -lt 0 -and $sw.Elapsed.TotalSeconds -lt $TimeoutSec) {
    if ($p.HasExited) { throw "Invoke-ChildFast: worker exited (code $($p.ExitCode))" }
    Start-Sleep -Milliseconds 10
  }
  if ($sw.Elapsed.TotalSeconds -ge $TimeoutSec) {
    $err = ""
    try { if ($p -and $p.StandardError.Peek() -ge 0) { $err = $p.StandardError.ReadToEnd() } } catch {}
    throw ("Invoke-ChildFast: worker timeout after {0}s{1}" -f $TimeoutSec, ($(if ($err) { " - stderr: $err" } else { "" })))
  }

  $line = $p.StandardOutput.ReadLine()
  return [int]$line
}

Export-ModuleMember -Function Invoke-ChildFast,Start-VEWorker,Stop-VEWorker

