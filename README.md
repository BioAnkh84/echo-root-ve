# Vulpine Echo Kernel v0.1a

PowerShell 5.1–safe test kernel for Echo Root OS (**ψ_min = 1.38**).

## Commands
- `.\ve_kernel.ps1 status` — prints READY
- `.\ve_kernel.ps1 exec "<cmd>"` — runs inline command
- `.\ve_kernel.ps1 audit` — silent self-test (exit code only)
- `.\ve_kernel.ps1 audit-verbose` — key=value test output

## Quickstart
```powershell
# status
.\ve_kernel.ps1 status

# exec
.\ve_kernel.ps1 exec '"hello world"'

# audit (quiet: exit code only)
.\ve_kernel.ps1 audit; $LASTEXITCODE

# audit-verbose (prints lines)
.\ve_kernel.ps1 audit-verbose
```

## Exit codes
- `0` = success
- `10/11` = literal check fail
- `99` = internal audit error
