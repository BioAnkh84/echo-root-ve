# run_all.ps1
# Chains: unblock → handshake → gatecheck → ledger append → sysinfo → quickcheck

# Make sure scripts aren't marked as downloaded
Get-ChildItem . -Filter *.ps1 | Unblock-File

# Execution
.\ve_syscheck.ps1
