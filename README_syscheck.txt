# VE Syscheck Add-on v0.1a

Adds:
- `ve_sysinfo.ps1` — system spec snapshot → `sysinfo.json`
- `ve_syscheck.ps1` — one-button: handshake → gatecheck → ledger append → sysinfo → quickcheck
- `run_all.ps1` — unblocks local scripts and runs `ve_syscheck.ps1`

**Use:** copy these files into your existing `VE_Test_Suite_v0.1a` folder, then run:
```powershell
cd "<your>\VE_Test_Suite_v0.1a"
.un_all.ps1
```
Created: 2025-10-28 09:02 
