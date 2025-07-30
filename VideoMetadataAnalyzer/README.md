# Video Bitrate Analyzer

This script (`video_analyzer.py`) is a Python-based tool for analyzing video files within a specified folder and its subfolders, and presenting them in a sorted list based on metadata elements like bitrate, file size, and duration.

## Features

*   **Comprehensive Video Analysis**: Calculates key metrics for video files, including bitrate, file size, and duration.
*   **Multiple Sorting Options**: Sorts the results based on different criteria:
    *   `bitrate`: From highest to lowest (default).
    *   `filesize`: From largest to smallest.
    *   `duration`: From longest to shortest.
*   **Recursive Scanning**: Automatically scans the specified folder and all its subdirectories for video files.
*   **Wide Format Support**: Recognizes a broad range of video file extensions, including `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, and `.webm`.
*   **User-Friendly Display**:
    *   Presents bitrates and file sizes in human-readable formats (e.g., Mbps, Gbps, MB, GB).
    *   Provides a clean, organized, and easy-to-read table of results.
*   **Output Customization**: Allows you to limit the number of results displayed, making it easier to focus on top entries.
*   **Robust Error Handling**: Gracefully handles issues like missing files or corrupted video data.
*   **Powered by FFprobe**: Utilizes the reliable `ffprobe` tool (part of the FFmpeg suite) for accurate video metadata extraction.

## Setup and Usage

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/vitorjna/Scripts.git
    cd Scripts/VideoMetadataAnalyzer
    ```

2.  **Install FFmpeg**:
    This script requires `ffprobe` to be installed and accessible in your system's PATH. `ffprobe` is included with FFmpeg.
    You can download FFmpeg from its official website: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
    Follow the installation instructions for your operating system to add `ffmpeg` and `ffprobe` to your system's PATH.

3.  **Running the Script**:
    Execute the `video_analyzer.py` script from your terminal, providing the path to the folder you want to analyze.

    ```bash
    python video_analyzer.py <folder_path> [-l LIMIT] [-s SORT_BY]
    ```

    *   `<folder_path>`: The required path to the folder containing video files you wish to analyze.
    *   `-l LIMIT`, `--limit LIMIT`: An optional number to limit the output lines printed.
    *   `-s SORT_BY`, `--sort SORT_BY`: Optional. Sort order for video files.
        *   `bitrate`: Sort by bitrate (highest to lowest, default).
        *   `filesize`: Sort by file size (highest to lowest).
        *   `duration`: Sort by duration (longest to shortest).

    **Example**:
    ```bash
    python video_analyzer.py C:\Users\YourUser\Videos -l 10 -s filesize
    ```
    This command will analyze video files in `C:\Users\YourUser\Videos` and its subfolders, displaying the top 10 videos by filesize.

    The script will output a sorted list of video files, showing their bitrate, size, duration, and filename.