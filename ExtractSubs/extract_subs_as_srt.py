#!/usr/bin/env python3
"""
Script to extract subtitles from MKV files and convert them from ASS to SRT format.
Supports drag and drop of files.
"""

import sys
import os
import subprocess
import re
import tempfile
import shutil


def extract_subtitles_with_ffmpeg(input_file, output_dir):
    """
    Extract subtitles from MKV file using ffmpeg.

    Args:
        input_file (str): Path to the input MKV file
        output_dir (str): Directory to save extracted subtitles

    Returns:
        str: Path to the extracted ASS file, or None if extraction failed
    """
    # Get the base name of the file without extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    ass_output_path = os.path.join(output_dir, f"{base_name}.ass")

    # Run ffmpeg to extract subtitles
    try:
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-map', '0:s:0',  # Map the first subtitle stream
            '-c:s', 'ass',
            ass_output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(ass_output_path):
            return ass_output_path
        else:
            print(f"Error extracting subtitles from {input_file}")
            print(f"FFmpeg stderr: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception while extracting subtitles: {e}")
        return None


def convert_ass_to_srt(ass_file_path):
    """
    Convert ASS subtitle file to SRT format.

    Args:
        ass_file_path (str): Path to the input ASS file

    Returns:
        str: Path to the output SRT file
    """
    srt_file_path = os.path.splitext(ass_file_path)[0] + ".srt"

    try:
        with open(ass_file_path, 'r', encoding='utf-8') as ass_file, \
             open(srt_file_path, 'w', encoding='utf-8') as srt_file:

            # Skip the header part of ASS file until we reach the events
            in_events = False
            subtitle_index = 1

            for line in ass_file:
                # Check if we've reached the events section
                if line.startswith('[Events]'):
                    in_events = True
                    continue

                # Process subtitle lines
                if in_events and line.startswith('Dialogue:'):
                    # Parse the dialogue line
                    parts = line.strip().split(',', 9)  # Split only on first 9 commas
                    if len(parts) >= 10:
                        # Extract timecodes and text
                        start_time = parts[1]
                        end_time = parts[2]
                        text = parts[9]

                        # Convert time format from ASS to SRT
                        start_time_srt = convert_time_format(start_time)
                        end_time_srt = convert_time_format(end_time)

                        # Clean up the text
                        clean_text = clean_subtitle_text(text)

                        # Write to SRT file
                        srt_file.write(f"{subtitle_index}\n")
                        srt_file.write(f"{start_time_srt} --> {end_time_srt}\n")
                        srt_file.write(f"{clean_text}\n\n")

                        subtitle_index += 1

        return srt_file_path
    except Exception as e:
        print(f"Error converting ASS to SRT: {e}")
        return None


def convert_time_format(ass_time):
    """
    Convert ASS time format to SRT time format.

    Args:
        ass_time (str): Time in ASS format (h:mm:ss.cc or h:mm:ss:cc)

    Returns:
        str: Time in SRT format (hh:mm:ss,mmm)
    """
    # ASS format: h:mm:ss.cc or h:mm:ss:cc
    # SRT format: hh:mm:ss,mmm

    # Split by either : or .
    parts = re.split('[:.]', ass_time)
    if len(parts) >= 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        # Centiseconds to milliseconds
        centiseconds = int(parts[3]) if len(parts) > 3 else 0
        milliseconds = centiseconds * 10

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    else:
        return ass_time


def clean_subtitle_text(text):
    """
    Clean subtitle text by removing formatting and animation effects.

    Args:
        text (str): Raw subtitle text with formatting

    Returns:
        str: Cleaned subtitle text
    """
    # Remove ASS formatting tags like {\fn...}{\fs...}{\c&...&}
    text = re.sub(r'\{[^}]*\}', '', text)

    # Remove karaoke effects (letter by letter appearance)
    # These are typically represented by \k, \K, \kf tags in ASS
    # But they're already removed by the previous regex

    # Remove any remaining newlines within a subtitle (they should be spaces)
    text = text.replace('\\N', ' ').replace('\\n', ' ')

    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def process_file(input_file):
    """
    Process a single MKV file to extract and convert subtitles.

    Args:
        input_file (str): Path to the input MKV file
    """
    print(f"Processing file: {input_file}")

    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract subtitles
        ass_file = extract_subtitles_with_ffmpeg(input_file, temp_dir)
        if not ass_file:
            print(f"Failed to extract subtitles from {input_file}")
            return False

        # Convert to SRT
        srt_file = convert_ass_to_srt(ass_file)
        if not srt_file:
            print(f"Failed to convert subtitles for {input_file}")
            return False

        # Move SRT file to the same directory as the input file
        input_dir = os.path.dirname(input_file)
        input_base_name = os.path.splitext(os.path.basename(input_file))[0]
        final_srt_path = os.path.join(input_dir, f"{input_base_name}.srt")

        try:
            shutil.move(srt_file, final_srt_path)
            print(f"Successfully created: {final_srt_path}")
            return True
        except Exception as e:
            print(f"Error moving SRT file: {e}")
            return False


def main():
    """
    Main function to process files passed as arguments.
    """
    # Check if files were passed as arguments
    if len(sys.argv) < 2:
        print("Usage: Drag and drop MKV files onto this script")
        print("Or run: python extract_subs_as_srt.py <file1.mkv> [file2.mkv] ...")
        return

    # Process each file
    files_processed = 0
    files_success = 0

    for file_path in sys.argv[1:]:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        if not file_path.lower().endswith('.mkv'):
            print(f"Skipping non-MKV file: {file_path}")
            continue

        files_processed += 1
        if process_file(file_path):
            files_success += 1

    print(f"\nProcessed {files_processed} MKV files")
    print(f"Successfully extracted subtitles from {files_success} files")


if __name__ == "__main__":
    main()