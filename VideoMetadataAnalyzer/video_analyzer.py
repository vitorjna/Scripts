import json
import os
import subprocess
import sys
import argparse

def get_video_info(file_path):
    """
    Gets video duration and file size using ffprobe.
    Returns (duration_seconds, file_size_bytes) or (None, None) if an error occurs.
    """
    try:
        # Get duration using ffprobe
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        duration = float(info['format']['duration'])

        # Get file size
        file_size = os.path.getsize(file_path)

        return duration, file_size
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error processing {file_path}: {e}")
        return None, None

def analyze_videos_in_folder(folder_path):
    """
    Analyzes video files in a given folder and its subfolders,
    calculates their bitrates, and returns a sorted list.
    """
    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm')
    video_files_data = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(video_extensions):
                file_path = os.path.join(root, file)
                duration, file_size = get_video_info(file_path)

                if duration is not None and file_size is not None and duration > 0:
                    # Bitrate in bits per second (bps)
                    # file_size is in bytes, duration in seconds
                    # 1 byte = 8 bits
                    bitrate_bps = (file_size * 8) / duration
                    video_files_data.append({
                        'path': file_path,
                        'duration': duration,
                        'file_size': file_size,
                        'bitrate_bps': bitrate_bps
                    })

    return video_files_data

def format_bitrate(bitrate_bps):
    """Formats bitrate into human-readable units (bps, Kbps, Mbps, Gbps)."""
    if bitrate_bps >= 1_000_000_000:
        return f"{bitrate_bps / 1_000_000_000:.2f} Gbps"
    elif bitrate_bps >= 1_000_000:
        return f"{bitrate_bps / 1_000_000:.2f} Mbps"
    elif bitrate_bps >= 1_000:
        return f"{bitrate_bps / 1_000:.2f} Kbps"
    else:
        return f"{bitrate_bps:.2f} bps"

def format_size(size_bytes):
    """Formats file size into human-readable units (Bytes, KB, MB, GB)."""
    if size_bytes >= 1_000_000_000:
        return f"{size_bytes / 1_000_000_000:.2f} GB"
    elif size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.2f} MB"
    elif size_bytes >= 1_000:
        return f"{size_bytes / 1_000:.2f} KB"
    else:
        return f"{size_bytes:.2f} Bytes"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Analyze video files in a folder and sort them by various criteria.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "folder_path",
        help="Path to the folder containing video files."
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        help="Optional. A number to limit the output lines printed."
    )
    parser.add_argument(
        "-s", "--sort",
        choices=['bitrate', 'filesize', 'duration'],
        default='bitrate',
        help="""Optional. Sort order for video files.
        'bitrate': Sort by bitrate (highest to lowest, default).
        'filesize': Sort by file size (highest to lowest).
        'duration': Sort by duration (longest to shortest)."""
    )

    args = parser.parse_args()

    target_folder = args.folder_path
    output_limit = args.limit
    sort_by = args.sort

    if not os.path.isdir(target_folder):
        print(f"Error: Folder '{target_folder}' not found.")
        sys.exit(1)

    print(f"Analyzing video files in: {target_folder}\n")
    video_data = analyze_videos_in_folder(target_folder)

    if video_data:
        # Apply sorting based on user's choice
        if sort_by == 'bitrate':
            video_data.sort(key=lambda x: x['bitrate_bps'], reverse=True)
            print("Video files by bitrate (highest to lowest):")
        elif sort_by == 'filesize':
            video_data.sort(key=lambda x: x['file_size'], reverse=True)
            print("Video files by file size (highest to lowest):")
        elif sort_by == 'duration':
            video_data.sort(key=lambda x: x['duration'], reverse=True)
            print("Video files by duration (longest to shortest):")

        print("-" * 80)
        max_index_width = len(str(len(video_data)))

        for i, video in enumerate(video_data):
            if output_limit is not None and i >= output_limit:
                break
            print(f"{str(i+1).rjust(max_index_width)}. Bitrate: {format_bitrate(video['bitrate_bps']):>12} | "
                  f"Size: {format_size(video['file_size']):>10} | "
                  f"Duration: {video['duration']:>10.2f}s | "
                  f"Path: {os.path.basename(video['path'])}")
        print("-" * 80)

    else:
        print("No video files found or processed in the specified folder.")
