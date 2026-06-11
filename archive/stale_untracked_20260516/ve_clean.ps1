param(
  [string]$RepoRoot = "E:\Echo_Nexus_Data\repos\echo-root-ve"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

$trash = @(
  "qc_out.txt",
  "ve_quickcheck.py.bak",
  "ve_quickcheck.py.bak2",
  "ve_quickcheck.py.bak3",
  "._probe_hashscheme.py"
)

$deleted = 0
foreach ($t in $trash) {
  $p = Join-Path $RepoRoot $t
  if (Test-Path -LiteralPath $p) {
    Remove-Item -LiteralPath $p -Force
    $deleted++
    Write-Host "🧹 Deleted: $t"
  }
}

Write-Host "✅ ve_clean done. Deleted $deleted item(s)."