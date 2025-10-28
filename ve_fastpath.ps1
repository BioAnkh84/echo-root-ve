function Start-VEWorker {
  param([switch]$PwshCore)
  if ($script:VE_Worker -and -not $script:VE_Worker.HasExited) { return $script:VE_Worker }
  $shell = if ($PwshCore) { "pwsh.exe" } else { "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" }
  $workerCode = '[Console]::InputEncoding=[Text.Encoding]::UTF8;[Console]::OutputEncoding=[Text.Encoding]::UTF8; while (($line=[Console]::In.ReadLine()) -ne $null){ try { $cmd=[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($line)); $Error.Clear(); $LASTEXITCODE=0; Invoke-Expression $cmd | Out-Null; $exit= if ($Error.Count > 0) {1} else { if ($LASTEXITCODE) { $LASTEXITCODE } else { 0 } }; [Console]::Out.WriteLine($exit) } catch { [Console]::Out.WriteLine(1) } }'
  $si = New-Object System.Diagnostics.ProcessStartInfo
  $si.FileName  = $shell
  $si.Arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -Command -'
  $si.UseShellExecute = $false
  $si.RedirectStandardInput  = $true
  $si.RedirectStandardOutput = $true
  $si.RedirectStandardError  = $true
  $si.CreateNoWindow         = $true
  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $si
  [void]$p.Start()
  $b64 = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($workerCode))
  $p.StandardInput.WriteLine($b64)
  $p.StandardInput.Flush()
  $script:VE_Worker = $p
  return $p
}

function Stop-VEWorker {
  if ($script:VE_Worker -and -not $script:VE_Worker.HasExited) { try { $script:VE_Worker.Kill() } catch {} }
  $script:VE_Worker = $null
}

function Invoke-ChildFast {
  param(
    [Parameter(Mandatory)][string]$Command,
    [switch]$NoGuard,
    [switch]$PwshCore
  )
  $needsGuard = $Command -match '(?i)\b(Set-Content|Add-Content|Out-File)\b|(?<!\S)(?:\d?>|>>)|\s--%\s'
  if (-not $NoGuard -and $needsGuard) {
    if (-not (Get-Command Assert-VeSafeWrite -ErrorAction SilentlyContinue)) { throw "Invoke-ChildFast: VE Guard not loaded." }
    Assert-VeSafeWrite $Command
  }
  $p = Start-VEWorker -PwshCore:$PwshCore
  $b64 = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
  $p.StandardInput.WriteLine($b64)
  $p.StandardInput.Flush()
  $line = $p.StandardOutput.ReadLine()
  return [int]$line
}
