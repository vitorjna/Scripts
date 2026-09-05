"""
Remux video files to remove EAC3, DTS, and other high-bitrate audio tracks when an AAC track is present.

WARNING:
The presence of an AAC track does NOT guarantee that it has the same audio content as the high-bitrate
track (for example, the AAC track could be in a different language or a commentary track).
Always verify audio tracks before running this tool.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

VIDEO_EXTENSIONS = {".mkv", ".mp4", ".m4v", ".mov", ".ts"}

HIGH_BITRATE_CODECS = {
    "eac3",     # Dolby Digital Plus / Enhanced AC-3
    "dts",      # DTS / DTS-HD MA / DTS:X
    "dca",      # DTS Coherent Acoustics (ffprobe alias)
    "truehd",   # Dolby TrueHD
    "mlp",      # Meridian Lossless Packing
    "flac",     # Free Lossless Audio Codec
}


def is_high_bitrate_audio(codec_name: str) -> bool:
    """Check if an audio codec is considered high-bitrate or uncompressed."""
    codec = codec_name.lower()
    return codec in HIGH_BITRATE_CODECS or codec.startswith("pcm_")


def get_streams(file_path: Path) -> list[dict]:
    """Retrieve stream metadata for a given media file using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "stream=index,codec_name,codec_type",
        "-of", "json",
        str(file_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(res.stdout).get("streams", [])


def inspect_audio_streams(streams: list[dict]) -> tuple[list[dict], bool, list[dict]]:
    """Evaluate audio streams. Returns (audio_streams, has_aac, remove_streams).

    According to script rules, high-bitrate tracks can only be removed if an AAC track is present.
    """
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    has_aac = any(s.get("codec_name", "").lower() == "aac" for s in audio_streams)
    remove_streams = [
        s for s in audio_streams
        if is_high_bitrate_audio(s.get("codec_name", ""))
    ] if has_aac else []
    return audio_streams, has_aac, remove_streams


def find_video_files(folder: Path) -> list[Path]:
    """Recursively find video files in folder and subfolders."""
    video_files: list[Path] = []
    for root, _, filenames in os.walk(folder):
        for name in filenames:
            p = Path(root) / name
            if p.suffix.lower() in VIDEO_EXTENSIONS and not p.stem.endswith("_remuxed"):
                video_files.append(p)
    return sorted(video_files)


def scan_folder(folder: Path) -> list[tuple[Path, list[dict]]]:
    """Scan folder and subfolders and present files with removable audio tracks."""
    target_dir = folder.resolve()
    if not target_dir.is_dir():
        print(f"Directory not found: {target_dir}")
        return []

    print(f"Scanning '{target_dir}' and subfolders for video files...")
    video_files = find_video_files(target_dir)

    if not video_files:
        print("No video files found.")
        return []

    print(f"Found {len(video_files)} video file(s). Inspecting audio tracks...")

    candidates: list[tuple[Path, list[dict]]] = []
    for vf in video_files:
        try:
            streams = get_streams(vf)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"  Warning: Could not probe '{vf.name}': {e}")
            continue

        audio_streams, has_aac, remove_streams = inspect_audio_streams(streams)
        if has_aac and remove_streams:
            candidates.append((vf, remove_streams))

    print()
    if not candidates:
        print("No files found with audio tracks that can be removed according to rules.")
        return []

    print(f"Found {len(candidates)} file(s) with audio tracks that can be removed:\n")
    for file_path, rem_streams in candidates:
        track_desc = ", ".join(f"#{s['index']}:{s.get('codec_name', '')}" for s in rem_streams)
        print(f"  - {file_path} [{track_desc}]")

    return candidates


def pause_for_exit():
    """Wait for user input before exiting so console output remains visible in spawned cmd windows."""
    try:
        input("\nPress Enter to exit...")
    except (EOFError, KeyboardInterrupt):
        pass


def remux_remove_high_bitrate_audio(input_file: Path, output_file: Path | None = None) -> bool:
    """Remux video file removing EAC3, DTS, and other high-bitrate audio tracks if an AAC track exists."""
    if not input_file.exists():
        print(f"File not found: {input_file}")
        return False

    print(f"\nProcessing: {input_file.name}")
    try:
        streams = get_streams(input_file)
    except subprocess.CalledProcessError as e:
        print(f"Error probing file {input_file.name}: {e}")
        return False

    audio_streams, has_aac, remove_streams = inspect_audio_streams(streams)
    audio_codecs = [s.get("codec_name", "").lower() for s in audio_streams]

    print(f"  Found {len(audio_streams)} audio stream(s): {audio_codecs}")

    if not has_aac:
        print("  Skipping: No AAC audio track found (doing nothing).")
        return False

    if not remove_streams:
        print("  Skipping: No high-bitrate audio tracks found to remove.")
        return False

    if output_file is None:
        output_file = input_file.with_name(f"{input_file.stem}_remuxed{input_file.suffix}")

    to_remove_desc = [f"#{s['index']}:{s.get('codec_name', '')}" for s in remove_streams]
    print(f"  Removing high-bitrate stream(s): {', '.join(to_remove_desc)}")
    print(f"  Remuxing to: {output_file.name} ...")

    cmd = ["ffmpeg", "-y", "-i", str(input_file), "-map", "0"]
    for s in remove_streams:
        cmd.extend(["-map", f"-0:{s['index']}"])
    cmd.extend(["-c", "copy", str(output_file)])

    subprocess.run(cmd, check=True)
    print(f"  Successfully remuxed: {output_file.name}")
    return True


def self_test():
    """Assertion-based check of stream evaluation, codec filtering, and scan logic."""
    assert is_high_bitrate_audio("eac3")
    assert is_high_bitrate_audio("dts")
    assert is_high_bitrate_audio("dca")
    assert is_high_bitrate_audio("truehd")
    assert is_high_bitrate_audio("mlp")
    assert is_high_bitrate_audio("flac")
    assert is_high_bitrate_audio("pcm_s16le")
    assert is_high_bitrate_audio("pcm_s24le")
    assert not is_high_bitrate_audio("aac")
    assert not is_high_bitrate_audio("ac3")
    assert not is_high_bitrate_audio("mp3")
    assert not is_high_bitrate_audio("opus")

    sample_streams = [
        {"index": 0, "codec_type": "video", "codec_name": "hevc"},
        {"index": 1, "codec_type": "audio", "codec_name": "aac"},
        {"index": 2, "codec_type": "audio", "codec_name": "eac3"},
        {"index": 3, "codec_type": "audio", "codec_name": "dts"},
        {"index": 4, "codec_type": "audio", "codec_name": "ac3"},
        {"index": 5, "codec_type": "subtitle", "codec_name": "subrip"},
    ]
    audio, has_aac, to_remove = inspect_audio_streams(sample_streams)
    assert has_aac is True
    assert [s["index"] for s in to_remove] == [2, 3]

    # Test case without AAC: should not mark anything for removal
    no_aac_streams = [
        {"index": 1, "codec_type": "audio", "codec_name": "eac3"},
        {"index": 2, "codec_type": "audio", "codec_name": "dts"},
    ]
    _, has_aac, to_remove = inspect_audio_streams(no_aac_streams)
    assert has_aac is False
    assert to_remove == []

    # Test case with AAC but no high-bitrate audio
    safe_streams = [
        {"index": 1, "codec_type": "audio", "codec_name": "aac"},
        {"index": 2, "codec_type": "audio", "codec_name": "ac3"},
    ]
    _, has_aac, to_remove = inspect_audio_streams(safe_streams)
    assert has_aac is True
    assert to_remove == []

    # Test recursive file discovery
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        sub = root / "subfolder"
        sub.mkdir()
        (root / "video1.mkv").touch()
        (root / "video1_remuxed.mkv").touch()
        (root / "ignore.txt").touch()
        (sub / "video2.mp4").touch()

        found = find_video_files(root)
        found_names = {f.name for f in found}
        assert found_names == {"video1.mkv", "video2.mp4"}

    print("Self-test passed.")


def main():
    if "--test" in sys.argv:
        self_test()
        return

    args = sys.argv[1:]

    # Check for scan mode: explicit --scan or run without any arguments / dropped files
    is_scan = False
    scan_target = Path.cwd()

    if not args:
        is_scan = True
    elif "--scan" in args:
        is_scan = True
        idx = args.index("--scan")
        if idx + 1 < len(args) and not args[idx + 1].startswith("-"):
            scan_target = Path(args[idx + 1])
    else:
        for arg in args:
            if arg.startswith("--scan="):
                is_scan = True
                scan_target = Path(arg.split("=", 1)[1])
                break

    if is_scan:
        scan_folder(scan_target)
        return

    # Process files (command line args or drag-and-drop)
    raw_args = [arg for arg in args if not arg.startswith("-")]
    target_files: list[Path] = []

    for arg in raw_args:
        p = Path(arg)
        if p.is_dir():
            target_files.extend(
                f for f in p.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
            )
        elif p.is_file():
            target_files.append(p)

    if not target_files:
        print("No video files found to process.")
        pause_for_exit()
        return

    print(
        "WARNING: The presence of an AAC track does not guarantee it shares the same audio content\n"
        "         as the high-bitrate track (e.g. it may be commentary or another language).\n"
        "         Always verify your tracks before remuxing.\n"
    )

    for target in target_files:
        remux_remove_high_bitrate_audio(target)

    pause_for_exit()


if __name__ == "__main__":
    main()
