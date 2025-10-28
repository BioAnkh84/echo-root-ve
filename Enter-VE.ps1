# Enter-VE.ps1 — jump into VE and load everything
Set-Location "$PSScriptRoot"
. .\ve_kernel.ps1
Import-Module ".\Modules\VE.Guard\VE.Guard.psd1" -Force
Write-Host "VE ready at: C:\Windows\system32"
Get-Command Invoke-Child, Invoke-ChildAsync | Format-Table -AutoSize
