@echo off
:: ============================================================
::  split_m4b_dnd.bat
::  Drag and drop an M4B file onto this script to split it
::  into one M4A file per chapter.
::
::  Requires: Python and ffmpeg/ffprobe on the PATH.
:: ============================================================

if "%~1"=="" (
    echo Drag and drop an M4B file onto this script to use it.
    pause
    goto :eof
)

python "%~dp0split_m4b_chapters.py" "%~1"
pause
