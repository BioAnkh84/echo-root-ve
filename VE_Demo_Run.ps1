# VE_Demo_Run.ps1 — safe demo (robust catch)
. "$PSScriptRoot\ve_kernel.ps1"
Import-Module "$PSScriptRoot\Modules\VE.Guard\VE.Guard.psd1" -Force

Write-Host "--- PASS: non-write commands ---"
Invoke-Child 'Write-Output "Hello World"'
Invoke-Child 'Write-Output "C:\Program Files\Common Files"'

Write-Host "
--- PASS: guarded write into .\ve_data ---"
Invoke-Child 'Set-Content -Path ".\ve_data\quoted name.txt" -Value "ok"'

Write-Host "
--- BLOCK: redirection/Out-File ---"
try {
  Invoke-Child 'Out-File ".\ve_data\oops.txt"'
} catch {
   = .Exception.Message
  if (-not ) {  = .ToString() }
  Write-Host "Blocked => " -ForegroundColor Yellow
}