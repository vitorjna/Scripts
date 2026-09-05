# Remove High Bitrate Audio Tracks

This script (`remove_high_bitrate_audio.py`) is a Python-based utility to remux video files (such as MKV or MP4) and remove redundant high-bitrate or lossless audio tracks (`EAC3`, `DTS`, `TrueHD`, `FLAC`, `PCM`), provided an `AAC` track is present in the file.

> [!WARNING]
> **Check your audio tracks before running this tool!**
> The presence of an AAC track does not guarantee that the AAC and the high-bitrate track have the same audio content (for example, the AAC track could be in a different language or a commentary track). Always inspect your media files before processing them.

## Features

*   **Safety Checks**: Confirms that both a high-bitrate stream to remove and an `AAC` stream to keep are present before performing any remuxing.
*   **Target Codecs**: Removes `EAC3` (Dolby Digital Plus), `DTS` / `DCA` (DTS-HD MA, DTS:X), `TrueHD` / `MLP`, `FLAC`, and `PCM` streams.
*   **Lossless Stream Copy**: Uses `ffmpeg` with `-c copy` so no video or audio re-encoding occurs.
*   **Full Preservation**: Keeps all video streams, subtitles, chapters, tags, and non-targeted audio tracks (e.g., AAC, AC3) intact.
*   **Scan Mode**: Quickly check folders and subfolders for candidate files containing removable tracks without remuxing.
*   **Batch & Drag-and-Drop**: Accepts individual files or drag-and-dropped files, pausing for user input before the command prompt closes.

## Requirements

*   **Python 3.10+**
*   **FFmpeg** & **FFprobe**: Must be installed and available on your system `PATH`.

## Usage

**Scan a Specific Folder & Subfolders:**
```bash
python remove_high_bitrate_audio.py --scan "path/to/folder"
```

**Scan Current Directory & Subfolders (Default when run without parameters):**
```bash
python remove_high_bitrate_audio.py
```

**Remux / Process Files (or Drag and Drop onto the script):**
```bash
python remove_high_bitrate_audio.py path/to/video.mkv [video2.mkv ...]
```

**Run Self-Test:**
```bash
python remove_high_bitrate_audio.py --test
```

