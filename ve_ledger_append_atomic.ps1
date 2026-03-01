# ve_ledger_append_atomic.ps1
# Purpose: Append ledger entry with hash chain using atomic write + named mutex
# Patch posture (v1.0.3):
#  - Stable UTF-8 hashing
#  - Optional *_bps fixed-point fields (basis points) while preserving legacy float fields
#  - Deterministic rounding (no locale formatting)
#  - Canonical JSON via System.Text.Json under pwsh (preferred)
#  - Write EXACT canonical JSON line to ledger so quickcheck recomputation matches

param(
    [string]$LedgerPath = "ledger.jsonl",

    # Legacy float fields (backwards compatible)
    [double]$rho = 0.81,
    [double]$gamma = 0.77,
    [double]$delta = 0.29,

    # Optional fixed-point basis points (preferred when explicitly provided)
    [Nullable[int]]$rho_bps = $null,
    [Nullable[int]]$gamma_bps = $null,
    [Nullable[int]]$delta_bps = $null,

    # Emit BPS fields even if only floats provided (defaults OFF)
    [switch]$EmitBps,

    [string]$actor = "VE",
    [string]$etype = "EVENT",
    [string]$consent = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\ve_atomic_io.ps1"

function Convert-ToStableJson {
    param([Parameter(Mandatory=$true)] $Obj)

    # Require System.Text.Json (pwsh / PS7+)
    $stj = [type]::GetType("System.Text.Json.JsonSerializer, System.Text.Json", $false)
    if (-not $stj) {
        throw "System.Text.Json not available. Run with pwsh (PowerShell 7+)."
    }

    $opt = [System.Text.Json.JsonSerializerOptions]::new()
    $opt.WriteIndented = $false
    $opt.Encoder = [System.Text.Encodings.Web.JavaScriptEncoder]::UnsafeRelaxedJsonEscaping
    return [System.Text.Json.JsonSerializer]::Serialize($Obj, $opt)
}

function Get-Sha256Utf8 {
    param([Parameter(Mandatory=$true)][string]$Text)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha.ComputeHash($bytes)
        return -join ($hashBytes | ForEach-Object { $_.ToString("x2") })
    }
    finally { $sha.Dispose() }
}

function Clamp-01([double]$x) {
    if ($x -lt 0.0) { return 0.0 }
    if ($x -gt 1.0) { return 1.0 }
    return $x
}
function Round2([double]$x) {
    return [math]::Round($x, 2, [MidpointRounding]::AwayFromZero)
}
function To-Bps([double]$x) {
    $c = Clamp-01 $x
    return [int][math]::Round($c * 10000.0, 0, [MidpointRounding]::AwayFromZero)
}
function From-Bps([int]$bps) {
    return ([double]$bps) / 10000.0
}

# Guard: single-writer using named mutex
$mutex = New-Object System.Threading.Mutex($false, "Global\VulpineEchoLedgerMutex")
$hasHandle = $false

try {
    $hasHandle = $mutex.WaitOne(5000)
    if (-not $hasHandle) { throw "Timeout acquiring ledger mutex" }

    # Genesis if missing
    if (-not (Test-Path $LedgerPath)) {
        $gen = [ordered]@{
            time      = (Get-Date).ToString("s")
            type      = "GENESIS"
            actor     = $actor
            event     = "INIT"
            consent   = $consent
            rho       = 0.0
            gamma     = 0.0
            delta     = 0.0
            hash_prev = ("0" * 64)
        }

        $jsonNoHash = Convert-ToStableJson $gen
        $gen["hash_self"] = Get-Sha256Utf8 $jsonNoHash

        $jsonLine = Convert-ToStableJson $gen
        Add-JsonLineAtomicallyText -Path $LedgerPath -Text $jsonLine
    }

    $prev = Read-LastJsonLine -Path $LedgerPath
    if (-not $prev) { throw "Ledger read failed or last line invalid JSON." }

    $prevHash = $prev.hash_self
    if (-not $prevHash) { $prevHash = ("0" * 64) }

    # NOTE: Nullable params may arrive as $null/int; avoid .HasValue
    $haveBps = (($null -ne $rho_bps) -and ($null -ne $gamma_bps) -and ($null -ne $delta_bps))

    if ($haveBps) {
        $rho   = From-Bps ([int]$rho_bps)
        $gamma = From-Bps ([int]$gamma_bps)
        $delta = From-Bps ([int]$delta_bps)
    } else {
        $rho_bps   = To-Bps $rho
        $gamma_bps = To-Bps $gamma
        $delta_bps = To-Bps $delta
    }

    $rho2   = Round2 (Clamp-01 $rho)
    $gamma2 = Round2 (Clamp-01 $gamma)
    $delta2 = Round2 (Clamp-01 $delta)

    $entry = [ordered]@{
        time      = (Get-Date).ToString("s")
        type      = $etype
        actor     = $actor
        consent   = $consent
        rho       = $rho2
        gamma     = $gamma2
        delta     = $delta2
        hash_prev = $prevHash
    }

    if ($haveBps -or $EmitBps.IsPresent) {
        $entry["rho_bps"]   = [int]$rho_bps
        $entry["gamma_bps"] = [int]$gamma_bps
        $entry["delta_bps"] = [int]$delta_bps
    }

    $jsonNoHash = Convert-ToStableJson $entry
    $entry["hash_self"] = Get-Sha256Utf8 $jsonNoHash

    $jsonLine = Convert-ToStableJson $entry
    Add-JsonLineAtomicallyText -Path $LedgerPath -Text $jsonLine

    Write-Host "Appended entry. hash_prev=$prevHash hash_self=$($entry.hash_self)"
}
finally {
    if ($hasHandle) { $mutex.ReleaseMutex() | Out-Null }
    $mutex.Dispose()
}
