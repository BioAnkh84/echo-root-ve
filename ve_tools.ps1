# ve_tools.ps1 — helpers around ve_kernel.ps1 (PS 5.1 safe)

# Resolve base folder from this script file when dot-sourced; fallback to CWD if null
$Script:VE_Base = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Script:VE_Base) { $Script:VE_Base = (Get-Location).Path }

$Script:Kernel   = Join-Path $Script:VE_Base 've_kernel.ps1'
$Script:SnapRoot = Join-Path $Script:VE_Base '.ve_snapshots'
$Script:DataRoot = Join-Path $Script:VE_Base 've_data'
$Script:Ledger   = Join-Path $Script:VE_Base 've_ledger.jsonl'

function Get-PythonPath {
  $c = Get-Command python -ErrorAction SilentlyContinue
  if ($c) { return $c.Path }
  $c = Get-Command py -ErrorAction SilentlyContinue
  if ($c) { return $c.Path }
  return $null
}

function Get-VELatestSeq {
  if (-not (Test-Path -LiteralPath $Script:Ledger)) { return 0 }
  $lines = Get-Content -LiteralPath $Script:Ledger -ErrorAction SilentlyContinue
  if (-not $lines) { return 0 }
  return ($lines | Where-Object { $_.Trim() } | Measure-Object).Count
}

function Get-VEHighestSnapSeq {
  if (-not (Test-Path -LiteralPath $Script:SnapRoot)) { return 0 }
  $dirs = Get-ChildItem -LiteralPath $Script:SnapRoot -Directory -ErrorAction SilentlyContinue |
          Where-Object { $_.Name -like 'seq-*' }
  if (-not $dirs) { return 0 }
  $nums = @()
  foreach ($d in $dirs) {
    $n = ($d.Name -replace '[^\d]', '')
    if ($n -match '^\d+$') { $nums += [int]$n }
  }
  if (-not $nums) { return 0 }
  ($nums | Measure-Object -Maximum).Maximum
}

function Invoke-VEAuditVerifyLatest {
  if (-not (Test-Path -LiteralPath $Script:Kernel)) { Write-Error "KERNEL_NOT_FOUND: $Script:Kernel"; return }
  $latest = Get-VELatestSeq
  if ($latest -le 0) { Write-Warning "No ledger yet."; return }

  # Prefer verifying the latest seq; if no snapshot for it, fall back to highest existing snapshot.
  $target = $latest
  $snapDir = Join-Path $Script:SnapRoot ("seq-{0:d4}" -f $target)
  $manPath = Join-Path $snapDir 'manifest.json'
  if (-not (Test-Path -LiteralPath $manPath)) {
    $fallback = Get-VEHighestSnapSeq
    if ($fallback -gt 0) {
      Write-Host ("(No snapshot for seq {0}; verifying highest existing snapshot {1})" -f $latest, $fallback)
      $target = $fallback
    } else {
      Write-Warning ("No snapshots exist. Create one:  & `"$Script:Kernel`" snap -Seq {0}" -f $latest)
      return
    }
  }

  & $Script:Kernel audit -VerifySeq $target
}

function Get-VESnapshotList {
  if (-not (Test-Path -LiteralPath $Script:SnapRoot)) { return @() }
  Get-ChildItem -LiteralPath $Script:SnapRoot -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like 'seq-*' } |
    Sort-Object Name |
    ForEach-Object {
      $seq = $_.Name -replace '[^\d]', ''
      $metaPath = Join-Path $_.FullName 'meta.json'
      $manPath  = Join-Path $_.FullName 'manifest.json'
      $count = '(n/a)'
      if (Test-Path -LiteralPath $manPath) {
        try {
          $raw = Get-Content $manPath -Raw | ConvertFrom-Json
          if ($raw -is [System.Collections.IEnumerable]) {
            $count = ($raw | Measure-Object).Count
          } elseif ($raw.PSObject.Properties.Name -contains 'files') {
            $count = ($raw.files | Measure-Object).Count
          } else {
            $count = 1
          }
        } catch { $count = '(bad manifest)' }
      }
      [pscustomobject]@{
        Seq         = [int]$seq
        Path        = $_.FullName
        Files       = $count
        HasMeta     = (Test-Path -LiteralPath $metaPath)
        HasManifest = (Test-Path -LiteralPath $manPath)
      }
    }
}

function Invoke-VERevertDryRun {
  param([Parameter(Mandatory=$true)][int]$Seq)
  $pyExe = Get-PythonPath
  if (-not $pyExe) { Write-Error "PYTHON_NOT_FOUND"; return }
  $ver = Join-Path $Script:VE_Base 've_manifest_verify.py'
  if (-not (Test-Path -LiteralPath $ver)) { Write-Error "VERIFIER_NOT_FOUND: $ver"; return }
  & $pyExe $ver --seq $Seq --data-root $Script:DataRoot --snap-root $Script:SnapRoot
}

function Invoke-VEPruneSnapshots {
  param([Parameter(Mandatory=$true)][int]$KeepLast)
  if ($KeepLast -lt 1) { Write-Error "KeepLast must be >= 1"; return }
  $list = Get-VESnapshotList | Sort-Object Seq
  $toKeep  = $list | Select-Object -Last $KeepLast
  $keepSet = @($toKeep.Seq)
  foreach ($row in $list) {
    if ($keepSet -notcontains $row.Seq) {
      Write-Host ("Removing old snapshot seq-{0:D4}" -f $row.Seq)
      Remove-Item -LiteralPath $row.Path -Recurse -Force -ErrorAction SilentlyContinue
    }
  }
  Write-Host ("Kept latest {0} snapshot(s)." -f $KeepLast)
}
