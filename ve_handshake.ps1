# ve_handshake.ps1
# Purpose: PowerShell → Python roundtrip sanity check (file-based, quote-safe, NO-BOM)

param(
    [string]$Id = "test-001",
    [double]$rho = 0.82,
    [double]$gamma = 0.79,
    [double]$delta = 0.27,
    [string]$Python = "python"
)

$payloadObj = @{
    id    = $Id
    rho   = $rho
    gamma = $gamma
    delta = $delta
}

$payloadJson = ($payloadObj | ConvertTo-Json -Compress)

$tmp = Join-Path $env:TEMP "ve_handshake_payload.json"

# Write UTF-8 without BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($tmp, $payloadJson, $utf8NoBom)

Write-Host "Payload JSON: $payloadJson"
Write-Host "Temp file: $tmp"
Write-Host "Running: $Python .\ve_handshake.py --input-file $tmp"

try {
    $args = @(".\ve_handshake.py", "--input-file", $tmp)
    $result = & $Python @args 2>&1
    Write-Host "`nPython returned:`n$result"
    exit $LASTEXITCODE
} catch {
    Write-Error "Failed to run ve_handshake.py: $_"
    exit 1
}