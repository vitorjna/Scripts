# Zip to 7z Converter

A multi-threaded Python script to convert `.zip` files into optimized `.7z` archives. It extracts files, recompresses them using 7-Zip's ultra compression (`-mx9`), verifies the integrity of the generated `.7z` files, and renames the original `.zip` file to `.bck`. Additionally, it includes a fallback mechanism to compress folders that contain only text-based files.

## Requirements

1. **Python 3.x**
2. **7-Zip** installed at the default location: `C:\Program Files\7-Zip\7z.exe`

## How It Works

For each `.zip` file found:
1. Extracts the archive into a temporary subfolder.
2. Recompresses the extracted contents into `<name>.zip.7z` using ultra compression (-mx9).
3. Tests the integrity of the resulting `.7z` archive.
4. If successful, renames the original `.zip` file to `<name>.bck` and cleans up the temporary folder.

**Fallback Mechanism:**
If a folder contains *only* text files (based on text extension rules like `.txt`, `.json`, `.csv`, `.py`, etc.), the script will compress the entire folder directly into a `.7z` archive and rename the original folder to `<foldername>.bck`.

Work is efficiently distributed across worker threads via a chunking algorithm to process files in parallel.

## Usage

### Command Line

You can run the script directly with Python:

```bash
python extract_and_recompress.py [folder] [arguments]
```

### Arguments

- `folder`: The target folder to process (defaults to current working directory).
- `-t`, `--threads`: Number of worker threads to spawn (default: 8).
- `--no-recursive`: Do not scan subdirectories.
- `-v`, `--verbose`: Enable verbose (debug) logging.

### Using the Batch File

The repository contains `extract_and_recompress.bat` which can be run in two ways:
- **Direct run**: Double-click it or run it in cmd to process the current folder.
- **Drag and drop**: Drag a folder and drop it onto the batch file to process that folder.
