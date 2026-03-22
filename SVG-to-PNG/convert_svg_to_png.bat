@echo off
set "PYTHON_EXE=C:\Program Files\Python314\python.exe"

if "%~1"=="" (
    echo Drag and drop SVG files onto this batch file to convert them.
    pause
    exit /b
)

"%PYTHON_EXE%" "%~dp0svg_to_png.py" %*
pause
