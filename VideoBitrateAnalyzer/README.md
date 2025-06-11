# Video Bitrate Analyzer

This script (`video_analyzer.py`) is a Python-based tool for analyzing video files within a specified folder and its subfolders, calculating their bitrates, and presenting them in a sorted list.

## Features

*   **Video Bitrate Calculation**: Computes the bitrate of various video formats (`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`).
*   **Recursive Folder Scan**: Scans the specified folder and all its subfolders for video files.
*   **Human-Readable Output**: Formats bitrates (bps, Kbps, Mbps, Gbps) and file sizes (Bytes, KB, MB, GB) for easy readability.
*   **Sorted Results**: Displays video files sorted by bitrate in descending order.
*   **Output Limiting**: Option to limit the number of displayed results.
*   **FFprobe Integration**: Leverages `ffprobe` (part of FFmpeg) to extract video duration.

## Setup and Usage

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/vitorjna/Scripts.git
    cd Scripts/VideoBitrateAnalyzer
    ```

2.  **Install FFmpeg**:
    This script requires `ffprobe` to be installed and accessible in your system's PATH. `ffprobe` is included with FFmpeg.
    You can download FFmpeg from its official website: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
    Follow the installation instructions for your operating system to add `ffmpeg` and `ffprobe` to your system's PATH.

3.  **Running the Script**:
    Execute the `video_analyzer.py` script from your terminal, providing the path to the folder you want to analyze.

    ```bash
    python video_analyzer.py <folder_path> [output_limit]
    ```

    *   `<folder_path>`: The required path to the folder containing video files you wish to analyze.
    *   `[output_limit]`: An optional number to limit the output lines printed.

    **Example**:
    ```bash
    python video_analyzer.py C:\Users\YourUser\Videos 10
    ```
    This command will analyze video files in `C:\Users\YourUser\Videos` and its subfolders, displaying the top 10 videos by bitrate.

    The script will output a sorted list of video files, showing their bitrate, size, duration, and filename.