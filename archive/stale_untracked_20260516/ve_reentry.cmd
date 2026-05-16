@echo off
setlocal
set "REPO=E:\Echo_Nexus_Data\repos\echo-root-ve"
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO%\ve_reentry.ps1"
set RC=%ERRORLEVEL%
echo.
echo [reentry] exitcode=%RC%
exit /b %RC%