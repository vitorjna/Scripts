import os
import sys
import resvg_py

def convert_svg_to_png(svg_path, max_width=1024, max_height=1024):
    try:
        # Generate output path
        base_name = os.path.splitext(svg_path)[0]
        png_path = f"{base_name}.png"

        # Use resvg-py to render directly to PNG
        # It handles scaling automatically to fit into the requested resolution
        # while maintaining aspect ratio when width and height are provided.
        png_bytes = resvg_py.svg_to_bytes(
            svg_path=svg_path,
            width=max_width,
            height=max_height
        )
        with open(png_path, 'wb') as f:
            f.write(png_bytes)
        print(f"Successfully converted (using resvg-py): {os.path.basename(svg_path)} -> {os.path.basename(png_path)}")
        return True
    except Exception as e:
        print(f"Error converting {svg_path}: {e}")
        return False

def main():
    # If no files are dragged and dropped, sys.argv will only contain the script name
    if len(sys.argv) < 2:
        print("Usage: Drag and drop SVG files onto this script.")
        input("Press Enter to exit...")
        return

    svg_files = [arg for arg in sys.argv[1:] if arg.lower().endswith('.svg')]

    if not svg_files:
        print("No SVG files found among the dropped files.")
        input("Press Enter to exit...")
        return

    print(f"Found {len(svg_files)} SVG file(s).")

    # Ask for resolution
    res_input = input("Enter target resolution (e.g., 1024x1024) or press Enter for default [1024x1024]: ").strip()

    width, height = 1024, 1024
    if res_input:
        try:
            if 'x' in res_input.lower():
                w_str, h_str = res_input.lower().split('x')
                width = int(w_str.strip())
                height = int(h_str.strip())
            else:
                width = height = int(res_input)
        except ValueError:
            print("Invalid resolution format. Using default 1024x1024.")

    print(f"Converting to {width}x{height}...")

    success_count = 0
    for svg_file in svg_files:
        if convert_svg_to_png(svg_file, width, height):
            success_count += 1

    print(f"\nFinished! Converted {success_count} of {len(svg_files)} files.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
