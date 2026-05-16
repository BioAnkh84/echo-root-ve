# ve_status.ps1
# Quick repo health / sync check for Vulpine Echo.

param(
    [string]$Root = $PSScriptRoot
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
Push-Location $rootPath
try {
    Write-Host "VE Status Check - $rootPath" -ForegroundColor Cyan

    if (Test-Path -LiteralPath ".\ve_kernel.ps1") {
        $kernelHash = (Get-FileHash -LiteralPath ".\ve_kernel.ps1" -Algorithm SHA256).Hash
        Write-Host "Kernel found - SHA256: $kernelHash"
    } else {
        Write-Host "Kernel missing (ve_kernel.ps1)" -ForegroundColor Red
    }

    if (Test-Path -LiteralPath ".\ve_ledger.jsonl") {
        $ledgerHash = (Get-FileHash -LiteralPath ".\ve_ledger.jsonl" -Algorithm SHA256).Hash
        $preview = Get-Content -LiteralPath ".\ve_ledger.jsonl" -TotalCount 1 -ErrorAction SilentlyContinue
        Write-Host "Ledger found - SHA256: $ledgerHash"
        Write-Host "Preview: $preview"
    } else {
        Write-Host "Ledger missing (ve_ledger.jsonl)" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "Git Status:" -ForegroundColor Yellow
    if (Get-Command git -ErrorAction SilentlyContinue) {
        git rev-parse --is-inside-work-tree *> $null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Not inside a Git worktree."
            Write-Host ""
            Write-Host "VE Status complete." -ForegroundColor Green
            return
        }

        git status --short

        Write-Host ""
        Write-Host "Last Commit:"
        git log -1 --oneline

        $tags = @(git tag --list "v*")
        if ($tags.Count -gt 0) {
            $latestTag = $tags[-1]
            $tagCommit = git rev-list -n 1 $latestTag
            Write-Host "Latest tag: $latestTag -> commit $tagCommit"
        } else {
            Write-Host "No tags found."
        }
    } else {
        Write-Host "git not available on PATH." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "VE Status complete." -ForegroundColor Green
} finally {
    Pop-Location
}
