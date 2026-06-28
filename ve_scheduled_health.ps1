param(
    [string]$PythonLauncher = "py",
    [string]$PythonVersion = "-3.11",
    [string]$OutputRoot = "",
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $RepoRoot "ve_data\scheduled_health"
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

$Stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$JsonPath = Join-Path $OutputRoot "health_$Stamp.json"
$MarkdownPath = Join-Path $OutputRoot "health_$Stamp.md"

function Invoke-VeHealthStep {
    param(
        [string]$Name,
        [string]$Executable,
        [string[]]$Arguments
    )

    $Started = Get-Date
    Push-Location $RepoRoot
    try {
        $Output = & $Executable @Arguments 2>&1 | Out-String
        $Code = if ($null -eq $LASTEXITCODE) { 0 } else { [int]$LASTEXITCODE }
    }
    catch {
        $Output = $_ | Out-String
        $Code = 1
    }
    finally {
        Pop-Location
    }
    $Ended = Get-Date

    [ordered]@{
        name = $Name
        command = "$Executable $($Arguments -join ' ')"
        exit_code = $Code
        started_at = $Started.ToUniversalTime().ToString("o")
        ended_at = $Ended.ToUniversalTime().ToString("o")
        duration_ms = [int]($Ended - $Started).TotalMilliseconds
        output = $Output.Trim()
    }
}

$Steps = New-Object System.Collections.Generic.List[object]

$Steps.Add((Invoke-VeHealthStep `
    -Name "git_status" `
    -Executable "git" `
    -Arguments @("status", "--short", "--branch")))

$Steps.Add((Invoke-VeHealthStep `
    -Name "repo_map" `
    -Executable $PythonLauncher `
    -Arguments @($PythonVersion, ".\echo_root_cli.py", "repo-map")))

if (-not $SkipTests) {
    $Steps.Add((Invoke-VeHealthStep `
        -Name "unit_tests" `
        -Executable $PythonLauncher `
        -Arguments @($PythonVersion, "-m", "unittest", "discover", "-s", "Tests")))
}

$Steps.Add((Invoke-VeHealthStep `
    -Name "ve_checks" `
    -Executable $PythonLauncher `
    -Arguments @($PythonVersion, ".github\ve_checks.py")))

$Steps.Add((Invoke-VeHealthStep `
    -Name "cli_proof" `
    -Executable $PythonLauncher `
    -Arguments @($PythonVersion, ".\echo_root_cli.py", "prove", "--reset")))

$Failed = @($Steps | Where-Object { $_.exit_code -ne 0 })
$Posture = if ($Failed.Count -eq 0) { "OK" } else { "ACTION_NEEDED" }

$Report = [ordered]@{
    event_type = "scheduled_health_check"
    timestamp = (Get-Date).ToUniversalTime().ToString("o")
    repo_root = $RepoRoot
    posture = $Posture
    failed_steps = @($Failed | ForEach-Object { $_.name })
    steps = $Steps
    boundary = "Scheduled health checks are evidence, not approval. They do not execute repo writes beyond generated ve_data health reports and demo receipts."
}

$Report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $JsonPath -Encoding UTF8

$Lines = New-Object System.Collections.Generic.List[string]
$Lines.Add("# Echo Root VE Scheduled Health Check")
$Lines.Add("")
$Lines.Add("- Timestamp: $($Report.timestamp)")
$Lines.Add("- Posture: $Posture")
$Lines.Add("- Repo: $RepoRoot")
$Lines.Add("- JSON: $JsonPath")
$Lines.Add("")
$Lines.Add("## Steps")
$Lines.Add("")
foreach ($Step in $Steps) {
    $Status = if ($Step.exit_code -eq 0) { "OK" } else { "FAIL" }
    $Lines.Add("- $($Step.name): $Status (exit $($Step.exit_code), $($Step.duration_ms) ms)")
}
$Lines.Add("")
$Lines.Add("## Boundary")
$Lines.Add("")
$Lines.Add($Report.boundary)

$Lines | Set-Content -LiteralPath $MarkdownPath -Encoding UTF8

Write-Output "posture=$Posture"
Write-Output "json=$JsonPath"
Write-Output "markdown=$MarkdownPath"

if ($Failed.Count -eq 0) {
    exit 0
}
exit 1
