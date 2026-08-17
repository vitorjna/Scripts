@echo off
setlocal

set "SCRIPT=%~dp0extract_and_recompress.py"

if "%~1" == "" (
    python "%SCRIPT%" "%CD%"
) else (
    python "%SCRIPT%" %*
)

pause
endlocal
