"""
split_m4b_chapters.py

Splits an M4B audiobook into one M4A file per chapter using ffmpeg.

Usage:
    python split_m4b_chapters.py "path/to/audiobook.m4b"

Requirements:
    ffmpeg and ffprobe must be installed and on the system PATH.
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def check_tool(name: str) -> bool:
    """Return True if the given command-line tool is available on the PATH."""
    try:
        subprocess.run(
            [name, "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def get_chapters(input_path: Path) -> list[dict]:
    """Use ffprobe to extract chapter metadata from the M4B file."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_chapters",
            str(input_path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    data = json.loads(result.stdout)
    return data.get("chapters", [])


def sanitize_filename(name: str) -> str:
    """Remove or replace characters that are invalid in Windows filenames."""
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = name.strip()
    return name or "Untitled"


def extract_chapter(input_path: Path, start: str, end: str, output_path: Path) -> bool:
    """Run ffmpeg to extract a single chapter as an M4A file. Returns True on success."""
    result = subprocess.run(
        [
            "ffmpeg",
            "-v", "quiet",
            "-y",
            "-i", str(input_path),
            "-ss", start,
            "-to", end,
            "-c", "copy",
            "-vn",
            str(output_path),
        ]
    )
    return result.returncode == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python split_m4b_chapters.py \"path/to/audiobook.m4b\"")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}")
        sys.exit(1)

    # Check dependencies
    for tool in ("ffmpeg", "ffprobe"):
        if not check_tool(tool):
            print(f"[ERROR] '{tool}' not found. Please install ffmpeg and ensure it is on your PATH.")
            sys.exit(1)

    # Create output directory next to the source file, named after it
    output_dir = input_path.parent / input_path.stem
    output_dir.mkdir(exist_ok=True)

    print(f"\n  Input  : {input_path}")
    print(f"  Output : {output_dir}\n")

    chapters = get_chapters(input_path)

    if not chapters:
        print("[ERROR] No chapters found in the file.")
        sys.exit(1)

    total = len(chapters)
    print(f"  Found {total} chapter(s).\n")

    for i, chapter in enumerate(chapters, start=1):
        start = chapter["start_time"]
        end = chapter["end_time"]

        tags = chapter.get("tags", {})
        title = tags.get("title") or f"Chapter_{i:03d}"
        safe_title = sanitize_filename(title)

        output_filename = f"{i:03d} - {safe_title}.m4a"
        output_path = output_dir / output_filename

        print(f"  [{i:03d}/{total}] {title}")
        print(f"    {start}  ->  {end}")
        print(f"    -> {output_filename}")

        success = extract_chapter(input_path, start, end, output_path)

        if success:
            print("    OK\n")
        else:
            print("    [WARN] ffmpeg returned a non-zero exit code for this chapter.\n")

    print(f"  Done! Files saved to:\n  {output_dir}\n")


if __name__ == "__main__":
    main()
