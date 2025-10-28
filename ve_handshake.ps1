# ve_handshake.ps1
# Purpose: PowerShell → Python roundtrip sanity check

param(
    [string]$Id = "test-001",
    [double]$rho = 0.82,
    [double]$gamma = 0.79,
    [double]$delta = 0.27
)

$payload = @{
    id = $Id
    rho = $rho
    gamma = $gamma
    delta = $delta
} | ConvertTo-Json -Compress

# Call Python script; adjust interpreter if needed (e.g., py / python3)
$cmd = @("python", "ve_handshake.py", "--input", $payload)
Write-Host "Running: $($cmd -join ' ')"

try {
    $result = & $cmd 2>&1
    Write-Host "`nPython returned:`n$result"
} catch {
    Write-Error "Failed to run ve_handshake.py: $_"
    exit 1
}
