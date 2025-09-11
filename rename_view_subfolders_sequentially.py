from pathlib import Path
from natsort import natsorted
import argparse

def rename_subfolders(base_path, start_id):
    if not base_path.is_dir():
        print(f"Error: {base_path} is not a directory.")
        return

    # Get subfolders only
    folders = [f for f in base_path.iterdir() if f.is_dir()]

    # Sort folders by natural sort
    sorted_folders = natsorted(folders, key=lambda x: x.name)

    # Determine digits (at least 2)
    total_folders = len(sorted_folders) + start_id
    digits = max(2, len(str(total_folders - 1)))

    # First pass: rename to temporary folder names
    temp_folders = []
    for i, folder in enumerate(sorted_folders):
        temp_path = folder.with_name(f"__temp_{i}__")
        folder.rename(temp_path)
        temp_folders.append(temp_path)

    # Second pass: rename to final format
    for i, folder in enumerate(temp_folders, start=start_id):
        new_name = f"view_{i:0{digits}d}.data"
        new_path = base_path / new_name
        folder.rename(new_path)
        print(f"Renamed: {folder.name} -> {new_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rename subfolders in sequential order using natural sort."
    )
    parser.add_argument(
        "base_dir",
        type=Path,
        help="Path to the base directory containing the subfolders."
    )
    parser.add_argument(
        "--start",
        default=0,
        type=int,
        help="Starting number for sequential subfolder naming."
    )

    args = parser.parse_args()
    rename_subfolders(args.base_dir, args.start)
