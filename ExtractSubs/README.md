# Extract Subtitles

This script (`extract_subs_as_srt.py`) is a Python-based tool for extracting subtitles from MKV files and converting them from ASS to SRT format.

## Features

*   **MKV Extraction**: Uses `ffmpeg` to extract the first subtitle stream from an MKV file.
*   **Format Conversion**: Automatically converts extracted ASS subtitles to the more widely compatible SRT format.
*   **Text Cleaning**: Removes ASS formatting tags, animation effects, and karaoke markers to ensure clean, readable SRT output.
*   **Timecode Conversion**: Handles the conversion between ASS time format (`h:mm:ss.cc`) and SRT time format (`hh:mm:ss,mmm`).
*   **Drag & Drop Support**: Designed for easy use on Windows by dragging MKV files directly onto the script or a batch file.

## Requirements

*   **FFmpeg**: Must be installed and available in your system's PATH.

## Usage

**Single or Multiple Files:**
```bash
python extract_subs_as_srt.py path/to/video.mkv [video2.mkv ...]
```

**Windows Drag & Drop:**
Simply drag one or more `.mkv` files onto the script.
