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
