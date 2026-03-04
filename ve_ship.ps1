# ve_ship.ps1
# PR-safe shipping helper for echo-root-ve (protected main friendly)
# Creates a timestamped branch, stages allowlisted files, commits, pushes, prints PR URL.

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [string]$Message,

  [string]$BranchPrefix = "ship",

  [string[]]$Files = @(
    "ve_syscheck.ps1",
    "ve_quickcheck.py",
    "ve_ledger_append.ps1",
    "ve_handshake.ps1",
    "ve_handshake.py",
    "ve_reentry.ps1",
    "ve_ship.ps1",
    ".gitignore",
    "README.md",
    "CHANGELOG.md",
    "SECURITY.md"
  ),

  [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Fail([string]$msg) {
  Write-Error $msg
  throw $msg
}

# Verify git exists
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Fail "git not found on PATH."
}

# Verify inside repo
$inside = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $inside.Trim() -ne "true") {
  Fail "Not inside a git repository."
}

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$now = Get-Date -Format "yyyyMMdd-HHmmss"
$branch = "$BranchPrefix/$now"

Write-Host "[ve_ship] repo: $repoRoot"
Write-Host "[ve_ship] branch: $branch"
Write-Host "[ve_ship] message: $Message"

if (-not $WhatIf) {
  git fetch --all --prune | Out-Null
}

# Create branch
if ($WhatIf) {
  Write-Host "[ve_ship] (whatif) git checkout -b $branch"
}
else {
  git checkout -b $branch
  if ($LASTEXITCODE -ne 0) {
    git checkout $branch
    if ($LASTEXITCODE -ne 0) {
      Fail "Failed to create/checkout branch $branch"
    }
  }
}

# Stage allowlisted files
$stagedAny = $false

foreach ($f in $Files) {

  $path = Join-Path $repoRoot $f
  if (-not (Test-Path $path)) { continue }

  $status = git status --porcelain -- "$f"

  if ($status) {

    if ($WhatIf) {
      Write-Host "[ve_ship] (whatif) git add -- $f"
    }
    else {
      git add -- "$f"
      if ($LASTEXITCODE -ne 0) {
        Fail "Failed to stage: $f"
      }
    }

    $stagedAny = $true
  }
}

if (-not $stagedAny) {
  Write-Host "[ve_ship] No allowlisted changes to commit. Nothing staged."
  return
}

# Commit
if ($WhatIf) {
  Write-Host "[ve_ship] (whatif) git commit -m `"$Message`""
}
else {
  git commit -m "$Message"
  if ($LASTEXITCODE -ne 0) {
    Fail "Commit failed."
  }
}

# Push
if ($WhatIf) {
  Write-Host "[ve_ship] (whatif) git push -u origin $branch"
}
else {
  git push -u origin $branch
  if ($LASTEXITCODE -ne 0) {
    Fail "Push failed."
  }
}

# Determine repo URL
$origin = (git remote get-url origin).Trim()
Write-Host "[ve_ship] origin: $origin"

$compareUrl = $null

if ($origin -match "^https://github\.com/([^/]+)/([^/]+?)(\.git)?$") {
  $owner = $Matches[1]
  $repo  = $Matches[2]

  $compareUrl = "https://github.com/$owner/$repo/compare/main...${branch}?expand=1"
}
elseif ($origin -match "^git@github\.com:([^/]+)/([^/]+?)(\.git)?$") {
  $owner = $Matches[1]
  $repo  = $Matches[2]

  $compareUrl = "https://github.com/$owner/$repo/compare/main...${branch}?expand=1"
}

Write-Host ""
Write-Host "[ve_ship] ✅ Shipped branch: $branch"

if ($compareUrl) {
  Write-Host "[ve_ship] Open PR: $compareUrl"
}
else {
  Write-Host "[ve_ship] Open PR: create PR from $branch into main."
}
