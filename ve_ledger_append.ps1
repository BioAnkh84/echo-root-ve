# ve_ledger_append.ps1
# Purpose: Append a trust-gated ledger entry with a SHA-256 hash chain

param(
    [string]$LedgerPath = "ledger.jsonl",
    [double]$rho = 0.81,
    [double]$gamma = 0.77,
    [double]$delta = 0.29
)

function Get-Sha256([string]$text) {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)
    ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
}

# Ensure ledger exists with a genesis entry
if (-not (Test-Path -Path $LedgerPath)) {
    $genesis = @{
        time = (Get-Date).ToString("s")
        type = "GENESIS"
        rho = 0.0; gamma = 0.0; delta = 0.0
        hash_prev = ("0" * 64)
    }
    $genesis.hash_self = Get-Sha256(($genesis | ConvertTo-Json -Compress))
    ($genesis | ConvertTo-Json -Compress) | Out-File -FilePath $LedgerPath -Encoding utf8
    Write-Host "Initialized new ledger with GENESIS record."
}

# Get previous hash_self
$lastLine = Get-Content $LedgerPath -Tail 1
try {
    $lastObj = $lastLine | ConvertFrom-Json
} catch {
    Write-Error "Last ledger line is not valid JSON. Aborting."
    exit 1
}
$prevHash = $lastObj.hash_self
if (-not $prevHash) { $prevHash = ("0" * 64) }

# Build new entry
$entry = @{
    time = (Get-Date).ToString("s")
    rho = [double]::Parse("{0:N2}" -f $rho)
    gamma = [double]::Parse("{0:N2}" -f $gamma)
    delta = [double]::Parse("{0:N2}" -f $delta)
    hash_prev = $prevHash
}

$json = ($entry | ConvertTo-Json -Compress)
$entry.hash_self = Get-Sha256($json)

# Re-serialize with hash_self
$jsonFinal = ($entry | ConvertTo-Json -Compress)

# Append
Add-Content -Path $LedgerPath -Value $jsonFinal
Write-Host "Appended entry with hash_prev=$prevHash"
Write-Host "hash_self=$($entry.hash_self)"
