# ve_ledger_append_atomic.ps1
# Purpose: Append ledger entry with hash chain using atomic write + named mutex

param(
    [string]$LedgerPath = "ledger.jsonl",
    [double]$rho = 0.81,
    [double]$gamma = 0.77,
    [double]$delta = 0.29,
    [string]$actor = "VE",
    [string]$etype = "EVENT",
    [string]$consent = ""
)

. "$PSScriptRoot\ve_atomic_io.ps1"

# Guard: single-writer using named mutex
$mutex = New-Object System.Threading.Mutex($false, "Global\VulpineEchoLedgerMutex")
$hasHandle = $false
try {
    $hasHandle = $mutex.WaitOne(5000) # 5s
    if (-not $hasHandle) { throw "Timeout acquiring ledger mutex" }

    # Genesis if missing
    if (-not (Test-Path $LedgerPath)) {
        $gen = @{
            time = (Get-Date).ToString("s")
            type = "GENESIS"
            actor = $actor
            event = "INIT"
            consent = $consent
            rho = 0.0; gamma = 0.0; delta = 0.0
            hash_prev = ("0" * 64)
        }
        $gen.hash_self = Get-Sha256(($gen | ConvertTo-Json -Compress))
        Add-JsonLineAtomically -Path $LedgerPath -Object $gen
    }

    $prev = Read-LastJsonLine -Path $LedgerPath
    if (-not $prev) { throw "Ledger read failed or last line invalid JSON." }
    $prevHash = $prev.hash_self
    if (-not $prevHash) { $prevHash = ("0" * 64) }

    $entry = @{
        time = (Get-Date).ToString("s")
        type = $etype
        actor = $actor
        consent = $consent
        rho = [double]::Parse("{0:N2}" -f $rho)
        gamma = [double]::Parse("{0:N2}" -f $gamma)
        delta = [double]::Parse("{0:N2}" -f $delta)
        hash_prev = $prevHash
    }
    $jsonNoHash = ($entry | ConvertTo-Json -Compress)
    $entry.hash_self = Get-Sha256($jsonNoHash)

    Add-JsonLineAtomically -Path $LedgerPath -Object $entry
    Write-Host "Appended entry. hash_prev=$prevHash hash_self=$($entry.hash_self)"
}
finally {
    if ($hasHandle) { $mutex.ReleaseMutex() | Out-Null }
    $mutex.Dispose()
}
