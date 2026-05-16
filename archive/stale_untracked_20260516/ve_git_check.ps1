# =========================================================
# VE Git Status Check (Fixed)
# =========================================================

Write-Host "`n==== VE Git Check ====" -ForegroundColor Cyan

# ---------------------------------------------------------
# 1. Confirm repo
# ---------------------------------------------------------
$repo = git rev-parse --show-toplevel 2>$null
if (-not $repo) {
    Write-Host "[ERROR] Not inside a git repo" -ForegroundColor Red
    exit
}
Write-Host "[OK] Repo root:" $repo -ForegroundColor Green

# ---------------------------------------------------------
# 2. Branch info
# ---------------------------------------------------------
$branch = git rev-parse --abbrev-ref HEAD
Write-Host "[INFO] Branch:" $branch -ForegroundColor Yellow

# ---------------------------------------------------------
# 3. Status (short)
# ---------------------------------------------------------
Write-Host "`n[CHANGES]" -ForegroundColor Yellow
git status --short

# ---------------------------------------------------------
# 4. Staged files
# ---------------------------------------------------------
Write-Host "`n[STAGED FILES]" -ForegroundColor Yellow
git diff --name-only --cached

# ---------------------------------------------------------
# 5. Unstaged diff summary
# ---------------------------------------------------------
Write-Host "`n[UNSTAGED DIFF]" -ForegroundColor Yellow
git diff --stat

# ---------------------------------------------------------
# 6. Last commit
# ---------------------------------------------------------
Write-Host "`n[LAST COMMIT]" -ForegroundColor Yellow
git log -1 --oneline

# ---------------------------------------------------------
# 7. Remote tracking
# ---------------------------------------------------------
Write-Host "`n[REMOTE STATUS]" -ForegroundColor Yellow
git status -sb

# ---------------------------------------------------------
# 8. Pending push check (FIXED)
# ---------------------------------------------------------
Write-Host "`n[CHECKING PUSH STATUS]" -ForegroundColor Yellow
git fetch origin 2>$null

$local  = git rev-parse "HEAD"
$remote = git rev-parse "@{u}" 2>$null

if ($remote) {
    if ($local -eq $remote) {
        Write-Host "[OK] Repo is up to date with origin" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Local branch differs from remote (push needed)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARN] No upstream set for this branch" -ForegroundColor Yellow
}

Write-Host "`n==== DONE ====" -ForegroundColor Cyan