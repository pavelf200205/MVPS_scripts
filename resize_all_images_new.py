from pathlib import Path
import argparse
import subprocess
import sys

# Supported image extensions (case-insensitive)
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".tiff", ".tif", ".bmp",
    ".webp", ".heic", ".heif", ".avif", ".jp2", ".j2k", ".jpf",
    ".jpx", ".jpm", ".svg", ".jxl"
}

def process_images(base_dir: Path, crop: str = None, resize: str = None):
    if not base_dir.is_dir():
        print(f"Error: {base_dir} is not a directory.")
        sys.exit(1)

    # Build mogrify command base
    cmd_base = ["magick", "mogrify"]
    if crop:
        cmd_base.extend(["-crop", crop])
    if resize:
        cmd_base.extend(["-resize", resize])
    
    cmd_base.extend(["-quality", "100"])

    # Process each folder separately (mogrify works in-place per folder)
    for folder in base_dir.rglob("*"):
        if folder.is_dir():
            images = [str(f) for f in folder.iterdir()
                      if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]
            if images:
                cmd = cmd_base + images
                print(f"Processing {len(images)} images in {folder}...")
                subprocess.run(cmd, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursively crop and/or resize images using ImageMagick's mogrify."
    )
    parser.add_argument(
        "base_dir",
        type=Path,
        help="Path to the base directory containing subfolders with images."
    )
    parser.add_argument(
        "--crop",
        type=str,
        help='Crop ROI, e.g., "512x512+256+256".'
    )
    parser.add_argument(
        "--resize",
        type=str,
        help='Resize size, e.g., "384x384".'
    )

    args = parser.parse_args()

    if not args.crop and not args.resize:
        parser.error("You must provide at least one of --crop or --resize.")

    process_images(args.base_dir, args.crop, args.resize)
