# ve_ledger_append.ps1
# Purpose: Append a trust-gated ledger entry with a SHA-256 hash chain (genesis-safe, deterministic)

param(
    [string]$LedgerPath = "E:\Echo_Nexus_Data\ve_ledger.jsonl",
    [double]$rho = 0.81,
    [double]$gamma = 0.77,
    [double]$delta = 0.29,
    [string]$Type = "SYS",
    [switch]$Genesis
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

function Ensure-LedgerFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType File -Path $Path -Force | Out-Null
    }
}

function Get-LastNonEmptyLine {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $lines = Get-Content -LiteralPath $Path -ErrorAction SilentlyContinue
    if (-not $lines) { return $null }
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $ln = $lines[$i]
        if ($ln -and $ln.Trim() -ne "") { return $ln.Trim() }
    }
    return $null
}

function Get-Sha256Hex {
    param([string]$Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        $hashBytes = $sha.ComputeHash($bytes)
        return -join ($hashBytes | ForEach-Object { $_.ToString("x2") })
    }
    finally {
        $sha.Dispose()
    }
}

function To-CanonicalOrdered {
    param([hashtable]$h)
    # deterministic key order
    $o = [ordered]@{}
    foreach ($k in ($h.Keys | Sort-Object)) {
        $o[$k] = $h[$k]
    }
    return $o
}

function Canonical-Json {
    param([hashtable]$h)
    # deterministic JSON string (sorted keys + compressed)
    $ordered = To-CanonicalOrdered -h $h
    return ($ordered | ConvertTo-Json -Compress -Depth 32)
}

function Compute-HashSelf {
    param([hashtable]$entry)
    # hash_self = sha256( canonical_json(entry WITHOUT hash_self) )
    $payload = @{}
    foreach ($k in $entry.Keys) {
        if ($k -ne "hash_self") { $payload[$k] = $entry[$k] }
    }
    $json = Canonical-Json -h $payload
    return Get-Sha256Hex -Text $json
}

function Now-UtcIso {
    # stable UTC timestamp with Z
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ")
}

# --- Main ---
$ZERO64 = ("0" * 64)

Ensure-LedgerFile -Path $LedgerPath

$lastLine = Get-LastNonEmptyLine -Path $LedgerPath
$ledgerHasRecord = [bool]$lastLine

# Determine prev hash (best effort)
$prevHash = $ZERO64
if ($ledgerHasRecord) {
    try {
        $lastObj = $lastLine | ConvertFrom-Json -ErrorAction Stop
        if ($lastObj -and $lastObj.PSObject.Properties.Name -contains "hash_self" -and $lastObj.hash_self) {
            $prevHash = [string]$lastObj.hash_self
        } else {
            $prevHash = $ZERO64
        }
    } catch {
        # if last line is junk, treat as broken tail
        $prevHash = $ZERO64
    }
}

# If ledger is empty OR forced genesis, write GENESIS first.
if ($Genesis -or -not $ledgerHasRecord) {
    $gen = @{
        time      = (Now-UtcIso)
        type      = "GENESIS"
        rho       = 0.0
        gamma     = 0.0
        delta     = 0.0
        hash_prev = $ZERO64
        hash_self = ""
    }
    $gen.hash_self = Compute-HashSelf -entry $gen
    $genLine = Canonical-Json -h $gen
    Add-Content -LiteralPath $LedgerPath -Value $genLine -Encoding utf8

    Write-Host "Initialized genesis entry."
    Write-Host "hash_self=$($gen.hash_self)"

    $prevHash = $gen.hash_self
}

# Append new entry
$entry = @{
    time      = (Now-UtcIso)
    type      = $Type
    rho       = [double]$rho
    gamma     = [double]$gamma
    delta     = [double]$delta
    hash_prev = $prevHash
    hash_self = ""
}

$entry.hash_self = Compute-HashSelf -entry $entry
$line = Canonical-Json -h $entry
Add-Content -LiteralPath $LedgerPath -Value $line -Encoding utf8

Write-Host "Appended entry with hash_prev=$prevHash"
Write-Host "hash_self=$($entry.hash_self)"
exit 0