# ve_sysinfo.ps1
# Collects non-sensitive system specs and writes sysinfo.json next to this script

param(
    [string]$OutPath = "sysinfo.json"
)

$sys = @{
    Computer = $env:COMPUTERNAME
    User     = $env:USERNAME
    OS       = (Get-CimInstance Win32_OperatingSystem).Caption
    Version  = (Get-CimInstance Win32_OperatingSystem).Version
    Build    = (Get-CimInstance Win32_OperatingSystem).BuildNumber
    CPU      = (Get-CimInstance Win32_Processor).Name
    Cores    = (Get-CimInstance Win32_Processor).NumberOfCores
    RAM_GB   = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
    GPU      = (Get-CimInstance Win32_VideoController | Select-Object -First 1 -ExpandProperty Name)
    Date     = (Get-Date).ToString("s")
}
$sys | ConvertTo-Json -Depth 4 | Out-File -Encoding utf8 $OutPath
Write-Host "✅ System snapshot written to $OutPath"
