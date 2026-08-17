#!/usr/bin/env python3
"""Convert every .zip file in a folder to .7z by extracting and recompressing.

For each zip file the script:
  1. Extracts the archive into a folder named after the zip.
  2. Recompresses the extracted contents into ``<zipname>.7z`` (-mx9).
  3. Tests the resulting 7z archive.
  4. Renames the original zip to ``<zipname>.bck``.
  5. Removes the temporary extraction folder.

Work is distributed across worker threads. The full file list is built first,
then split into ``max_threads * 10`` chunks so that when a thread finishes a
chunk it picks up the next one.
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"
DEFAULT_THREADS = 8

# File extensions treated as "text" for the folder fallback mechanism.
TEXT_EXTENSIONS = {
    ".txt", ".log", ".csv", ".tsv", ".json", ".xml", ".yaml", ".yml",
    ".md", ".rst", ".ini", ".cfg", ".conf", ".properties", ".toml",
    ".html", ".htm", ".css", ".js", ".ts", ".py", ".java", ".kt",
    ".c", ".cpp", ".cc", ".h", ".hpp", ".cs", ".go", ".rs", ".rb",
    ".php", ".pl", ".sh", ".bat", ".ps1", ".sql", ".gradle",
}

logger = logging.getLogger(__name__)


def find_zip_files(folder, recursive=True):
    if not recursive:
        return [
            os.path.join(folder, name)
            for name in os.listdir(folder)
            if name.lower().endswith(".zip")
            and os.path.isfile(os.path.join(folder, name))
        ]

    zip_files = []
    for root, _dirs, names in os.walk(folder):
        for name in names:
            if name.lower().endswith(".zip"):
                path = os.path.join(root, name)
                if os.path.isfile(path):
                    zip_files.append(path)
    return zip_files


def is_text_only_folder(folder):
    """Return True if *folder* contains at least one file and every file
    (recursively) has a text-file extension."""
    has_file = False
    for _root, _dirs, names in os.walk(folder):
        for name in names:
            has_file = True
            if os.path.splitext(name)[1].lower() not in TEXT_EXTENSIONS:
                return False
    return has_file


def find_text_folders(folder, recursive=True):
    """Find subfolders of *folder* that contain only text files.

    A text-only folder is selected as a whole; the search does not descend
    into it. Folders that are not text-only are descended into (when
    *recursive*) to look for text-only subfolders. Backup folders (``.bck``)
    are ignored.
    """
    result = []
    for entry in sorted(os.listdir(folder)):
        path = os.path.join(folder, entry)
        if not os.path.isdir(path) or entry.lower().endswith(".bck"):
            continue
        if is_text_only_folder(path):
            result.append(path)
        elif recursive:
            result.extend(find_text_folders(path, recursive=True))
    return result


def chunkify(items, num_chunks):
    """Split *items* into at most *num_chunks* roughly equal chunks."""
    num_chunks = max(1, min(num_chunks, len(items))) if items else 0
    chunks = [[] for _ in range(num_chunks)]
    for index, item in enumerate(items):
        chunks[index % num_chunks].append(item)
    return chunks


def compress_and_test(output_7z, source):
    """Compress *source* into *output_7z* (-mx9) and test the archive.

    Returns True on success.
    """
    compress = subprocess.run(
        [SEVEN_ZIP, "a", "-bb0", "-mx9", output_7z, source],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    test = subprocess.run(
        [SEVEN_ZIP, "t", "-bb0", output_7z],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return compress.returncode == 0 and test.returncode == 0


def process_file(zip_file):
    logger.debug("Processing file: %s", zip_file)

    folder = os.path.dirname(zip_file)
    base_name = os.path.splitext(os.path.basename(zip_file))[0]
    extract_folder = os.path.join(folder, base_name)
    output_7z = zip_file + ".7z"

    os.makedirs(extract_folder, exist_ok=True)

    extract = subprocess.run(
        [SEVEN_ZIP, "x", "-bb0", zip_file, f"-o{extract_folder}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if extract.returncode != 0:
        logger.error("Failed to extract \"%s\".", zip_file)
        return False

    if not compress_and_test(output_7z, os.path.join(extract_folder, "*")):
        logger.error("Failed to compress files into \"%s\".", output_7z)
        shutil.rmtree(extract_folder, ignore_errors=True)
        if os.path.exists(output_7z):
            os.remove(output_7z)
        return False

    shutil.rmtree(extract_folder, ignore_errors=True)
    os.replace(zip_file, os.path.join(folder, base_name + ".bck"))

    logger.debug("Successfully recompressed \"%s\" to \"%s\"", zip_file, output_7z)
    return True


def process_text_folder(text_folder):
    logger.debug("Processing text folder: %s", text_folder)

    parent = os.path.dirname(text_folder)
    base_name = os.path.basename(text_folder)
    output_7z = text_folder + ".7z"

    if not compress_and_test(output_7z, os.path.join(text_folder, "*")):
        logger.error("Failed to compress text folder into \"%s\".", output_7z)
        if os.path.exists(output_7z):
            os.remove(output_7z)
        return False

    os.replace(text_folder, os.path.join(parent, base_name + ".bck"))

    logger.debug("Successfully compressed text folder \"%s\" to \"%s\"", text_folder, output_7z)
    return True


def process_chunk(chunk, chunk_number, total_chunks, processor):
    logger.info(f"Thread processing chunk {chunk_number}/{total_chunks} with {len(chunk)} item(s)")
    for item in chunk:
        try:
            processor(item)
        except Exception:  # noqa: BLE001 - keep workers alive
            logger.exception("Error processing \"%s\"", item)

    logger.info(f"Finished processing chunk {chunk_number}/{total_chunks}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert zip files in a folder to 7z by extract + recompress."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=os.getcwd(),
        help="Folder to process (defaults to the current working directory).",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=DEFAULT_THREADS,
        help=f"Number of worker threads (default: {DEFAULT_THREADS}).",
    )
    parser.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="Only process the top-level folder, ignoring subfolders.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(threadName)s: %(message)s",
    )

    folder = os.path.abspath(args.folder)
    if not os.path.isdir(folder):
        logger.error("Not a folder: %s", folder)
        return 1

    if not os.path.isfile(SEVEN_ZIP):
        logger.error("7-Zip not found at: %s", SEVEN_ZIP)
        return 1

    max_threads = max(1, args.threads)

    def run_pass(items, processor, label):
        if not items:
            return
        logger.info(f"Found {len(items)} {label}. Using {max_threads} thread(s).")
        chunks = chunkify(items, max_threads * 10)
        total_chunks = len(chunks)
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for chunk_number, chunk in enumerate(chunks, start=1):
                executor.submit(process_chunk, chunk, chunk_number, total_chunks, processor)

    zip_files = find_zip_files(folder, recursive=args.recursive)
    run_pass(zip_files, process_file, "zip file(s)")

    # Fallback: compress folders that contain only text files directly to 7z.
    text_folders = find_text_folders(folder, recursive=args.recursive)
    run_pass(text_folders, process_text_folder, "text-only folder(s)")

    if not zip_files and not text_folders:
        logger.warning("No zip files or text-only folders found in: %s", folder)
        return 0

    logger.info("All files processed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
