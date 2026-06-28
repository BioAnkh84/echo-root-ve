# Scheduled Health Checks

`ve_scheduled_health.ps1` runs a bounded evidence check for Echo-Root-VE.

It does not grant authority, approve changes, push code, mutate memory, or run
an autonomous repair loop. It only collects evidence and writes local runtime
reports under ignored `ve_data/scheduled_health/`.

## What It Runs

- `git status --short --branch`
- `py -3.11 .\echo_root_cli.py repo-map`
- `py -3.11 -m unittest discover -s Tests`
- `py -3.11 .github\ve_checks.py`
- `py -3.11 .\echo_root_cli.py prove --reset`

The report posture is:

- `OK` when every step exits successfully
- `ACTION_NEEDED` when any step fails

## Manual Run

```powershell
powershell -ExecutionPolicy Bypass -File .\ve_scheduled_health.ps1
```

For a faster smoke check that skips the standalone unit-test step:

```powershell
powershell -ExecutionPolicy Bypass -File .\ve_scheduled_health.ps1 -SkipTests
```

`ve_checks.py` still runs tests, so `-SkipTests` only avoids the extra direct
test pass.

## Optional Windows Task Scheduler

Review the command before registering it. This changes local machine state.

Example daily task:

```powershell
$Action = New-ScheduledTaskAction `
  -Execute "powershell.exe" `
  -Argument "-ExecutionPolicy Bypass -File E:\Echo_Nexus_Data\repos\echo-root-ve\ve_scheduled_health.ps1"

$Trigger = New-ScheduledTaskTrigger -Daily -At 9am

Register-ScheduledTask `
  -TaskName "EchoRootVE-DailyHealth" `
  -Action $Action `
  -Trigger $Trigger `
  -Description "Run Echo Root VE bounded health evidence check"
```

## Boundary

Scheduled health is evidence, not permission.

An `OK` report means the checked commands passed at that time. It does not mean
the repo is release-approved, compliant, production-safe, or authorized for
publishing.

An `ACTION_NEEDED` report should prompt human review. The task should not fix
the repo automatically.
