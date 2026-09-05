@echo off
setlocal
title VHDX Compactor

:: Checked before elevating: the elevated relaunch has no console to report this back on
if "%~1"=="" (
    echo No file detected! 
    echo Please drag and drop a .vhdx or .vhd file directly onto this batch file icon.
    pause
    exit /b 1
)

if not exist "%~f1" (
    echo File not found:
    echo "%~f1"
    pause
    exit /b 1
)

:: Check for administrative privileges (Diskpart requires them)
net session >nul 2>&1
if errorlevel 1 (
    echo Requesting administrative privileges...
    :: Relaunched through cmd.exe because Start-Process cannot pass quoted arguments
    :: to a .bat; %~f1 because elevation resets the working directory
    powershell -NoProfile -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c \"\"%~f0\" \"%~f1\"\"' -Verb RunAs"
    exit /b
)

echo ===================================================
echo VHDX Compactor
echo ===================================================
echo.
echo Preparing to compact:
echo "%~f1"
echo.
echo IMPORTANT: Make sure the virtual machine or WSL instance using
echo this file is completely SHUT DOWN before continuing. 
echo (For WSL2, open a standard command prompt and run: wsl --shutdown)
echo.
pause

:: Create a temporary diskpart script. Redirection goes first so no trailing space
:: ends up inside the diskpart command lines.
set "tempScript=%TEMP%\compact_vdisk_%RANDOM%.txt"

>"%tempScript%" echo select vdisk file="%~f1"
>>"%tempScript%" echo attach vdisk readonly
>>"%tempScript%" echo compact vdisk
>>"%tempScript%" echo detach vdisk

echo.
echo Running Diskpart to compact the disk...
echo This may take a few minutes depending on the file size.
echo.

:: Run diskpart with the temporary script
diskpart /s "%tempScript%"
set "diskpartResult=%errorlevel%"

:: Clean up the temporary script
del "%tempScript%" >nul 2>&1

echo.
if %diskpartResult% neq 0 (
    echo Diskpart reported an error ^(code %diskpartResult%^).
    echo Make sure the disk is not mounted or in use by a running VM/WSL instance.
) else (
    echo Process completed! You can check the new file size.
)
pause