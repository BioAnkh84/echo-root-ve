# ve_ledger_append_atomic.ps1
# Purpose: Append ledger entry with hash chain using atomic write + named mutex
# Patch posture (v1.0.3):
#  - Stable UTF-8 hashing
#  - Optional *_bps fixed-point fields (basis points) while preserving legacy float fields
#  - Deterministic rounding (no locale formatting)
#  - Stable JSON serialization:
#       * PowerShell 7+ : System.Text.Json (preferred)
#       * PowerShell 5.1: Newtonsoft.Json if available (optional); otherwise fail loudly

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

    # Emit BPS fields even if only floats provided (defaults OFF to avoid changing output shape silently)
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

    # Prefer System.Text.Json when available (PowerShell 7+)
    $stj = [type]::GetType("System.Text.Json.JsonSerializer, System.Text.Json", $false)
    if ($stj) {
        $opt = [System.Text.Json.JsonSerializerOptions]::new()
        $opt.WriteIndented = $false
        $opt.Encoder = [System.Text.Encodings.Web.JavaScriptEncoder]::UnsafeRelaxedJsonEscaping
        return [System.Text.Json.JsonSerializer]::Serialize($Obj, $opt)
    }

    # Optional fallback: Newtonsoft.Json (PowerShell 5.1)
    try {
        Add-Type -AssemblyName "Newtonsoft.Json" -ErrorAction Stop | Out-Null
        $settings = New-Object Newtonsoft.Json.JsonSerializerSettings
        $settings.Formatting = [Newtonsoft.Json.Formatting]::None
        $settings.StringEscapeHandling = [Newtonsoft.Json.StringEscapeHandling]::Default
        return [Newtonsoft.Json.JsonConvert]::SerializeObject($Obj, $settings)
    } catch {
        throw "No stable JSON serializer available. Run with PowerShell 7+ (pwsh), or provide Newtonsoft.Json for PS5.1. Details: $($_.Exception.Message)"
    }
}

function Get-Sha256Utf8 {
    param([Parameter(Mandatory=$true)][string]$Text)

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha.ComputeHash($bytes)
        return -join ($hashBytes | ForEach-Object { $_.ToString("x2") })
    }
    finally {
        $sha.Dispose()
    }
}

function Clamp-01 {
    param([double]$x)
    if ($x -lt 0.0) { return 0.0 }
    if ($x -gt 1.0) { return 1.0 }
    return $x
}

function Round2 {
    param([double]$x)
    return [math]::Round($x, 2, [MidpointRounding]::AwayFromZero)
}

function To-Bps {
    param([double]$x)
    $c = Clamp-01 $x
    return [int][math]::Round($c * 10000.0, 0, [MidpointRounding]::AwayFromZero)
}

function From-Bps {
    param([int]$bps)
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

        Add-JsonLineAtomically -Path $LedgerPath -Object $gen
    }

    $prev = Read-LastJsonLine -Path $LedgerPath
    if (-not $prev) { throw "Ledger read failed or last line invalid JSON." }

    $prevHash = $prev.hash_self
    if (-not $prevHash) { $prevHash = ("0" * 64) }

    # Decide whether bps are the source of truth (only if ALL provided)
    $haveBps = ($rho_bps.HasValue -and $gamma_bps.HasValue -and $delta_bps.HasValue)

    if ($haveBps) {
        $rho   = From-Bps $rho_bps.Value
        $gamma = From-Bps $gamma_bps.Value
        $delta = From-Bps $delta_bps.Value
    } else {
        # Compute bps deterministically from floats, but only emit if EmitBps is set
        $rho_bps   = [Nullable[int]](To-Bps $rho)
        $gamma_bps = [Nullable[int]](To-Bps $gamma)
        $delta_bps = [Nullable[int]](To-Bps $delta)
    }

    # Canonicalize floats to 2 decimals (legacy intent)
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
        $entry["rho_bps"]   = $rho_bps.Value
        $entry["gamma_bps"] = $gamma_bps.Value
        $entry["delta_bps"] = $delta_bps.Value
    }

    $jsonNoHash = Convert-ToStableJson $entry
    $entry["hash_self"] = Get-Sha256Utf8 $jsonNoHash

    Add-JsonLineAtomically -Path $LedgerPath -Object $entry
    Write-Host "Appended entry. hash_prev=$prevHash hash_self=$($entry.hash_self)"
}
finally {
    if ($hasHandle) { $mutex.ReleaseMutex() | Out-Null }
    $mutex.Dispose()
}
