# Split M4B

A simple tool to split an M4B audiobook file into individual M4A files, one for each chapter, using `ffmpeg`.

## Features
- Extracts chapter metadata using `ffprobe`.
- Creates a new directory named after the audiobook to store the extracted chapters.
- Names each output file sequentially, preserving the chapter title (e.g., `001 - Prologue.m4a`).
- Provides a drag-and-drop batch script for easy Windows usage.

## Prerequisites
1. **Python 3** installed and on your system `%PATH%`.
2. **ffmpeg** and **ffprobe** installed and on your system `%PATH%`.
   - You can download ffmpeg from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or use a package manager like `winget` or `scoop`.

## Usage

### Method 1: Drag and Drop (Windows)
The easiest way to use the script on Windows is with the provided `.bat` file:
1. Locate your `.m4b` audiobook file.
2. Drag and drop the `.m4b` file directly onto the `split_m4b_dnd.bat` file.
3. A command prompt will open showing the progress of the extraction.

### Method 2: Command Line
You can also run the Python script directly from your terminal or command prompt:

```bash
python split_m4b_chapters.py "path/to/audiobook.m4b"
```

## Output
The script will create a new folder in the same directory as your source `.m4b` file. This folder will have the same name as the audiobook and will contain all the split `.m4a` files.
