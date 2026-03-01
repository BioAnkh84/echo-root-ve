# ve_atomic_io.ps1
# Utility: atomic JSONL writes + safe last-line read

function Get-Sha256([string]$text) {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)
    ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
}

function Test-FileLocked {
    param([string]$Path)
    try {
        $fs = [System.IO.File]::Open($Path, 'Open', 'Read', 'None')
        $fs.Close()
        return $false
    } catch {
        return $true
    }
}

function Read-LastJsonLine {
    param([string]$Path)
    if (!(Test-Path $Path)) { return $null }
    $line = Get-Content $Path -Tail 1 -ErrorAction Stop
    try { return $line | ConvertFrom-Json } catch { return $null }
}

function Add-JsonLineAtomically {
    param(
        [string]$Path,
        [hashtable]$Object
    )
    $dir = Split-Path -Parent $Path
    if ($dir -and !(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }

    $json = ($Object | ConvertTo-Json -Compress)
    $tmp = "$Path.tmp"
    # Create temp by copying original (if exists), then append new line, then atomic replace
    if (Test-Path $Path) {
        Copy-Item $Path $tmp -Force
    } else {
        New-Item -ItemType File -Path $tmp | Out-Null
    }
    Add-Content -Path $tmp -Value $json
    # Replace original atomically
    Move-Item -Path $tmp -Destination $Path -Force
}

function Add-JsonLineAtomicallyText {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Text
    )

    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }

    $tmp = "$Path.tmp.$([guid]::NewGuid().ToString('N'))"

    # Copy existing ledger to temp first (preserves previous content exactly)
    if (Test-Path $Path) {
        [System.IO.File]::Copy($Path, $tmp, $true)
    } else {
        # Ensure temp exists as empty file
        [System.IO.File]::WriteAllBytes($tmp, @())
    }

    # Append exact bytes (UTF-8, no BOM), always newline-terminated
    $line = $Text.TrimStart([char]0xFEFF).TrimEnd("`r","`n") + "`n"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($line)
    $fs = [System.IO.File]::Open($tmp, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write, [System.IO.FileShare]::Read)
    try {
        $fs.Write($bytes, 0, $bytes.Length)
        $fs.Flush($true)
    } finally {
        $fs.Dispose()
    }

    # Atomic replace on same volume via rename
    Move-Item -Force -Path $tmp -Destination $Path
}

