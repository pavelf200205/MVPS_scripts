from pathlib import Path
from natsort import natsorted
import argparse

def rename_sequentially(base_path, start_id):
    if not base_path.is_dir():
        print(f"Error: {base_path} is not a directory.")
        return

    # Get all files in the directory (not folders)
    files = [f for f in base_path.iterdir() if f.is_file()]

    # Sort by natural sort on file *stem* (name without extension)
    sorted_files = natsorted(files, key=lambda x: x.stem)

    # Determine number of digits (at least 2)
    total_files = len(sorted_files) + start_id
    digits = max(2, len(str(total_files - 1)))

    # First pass: rename to temporary names to avoid conflicts
    temp_files = []
    for i, file in enumerate(sorted_files):
        temp_path = file.with_name(f"__temp_{i}__{file.suffix}")
        file.rename(temp_path)
        temp_files.append(temp_path)

    # Second pass: rename to final sequential names
    for i, file in enumerate(temp_files, start=start_id):
        new_name = f"{i:0{digits}d}{file.suffix.lower()}"
        new_path = base_path / new_name
        file.rename(new_path)
        print(f"Renamed: {file.name} -> {new_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rename files sequentially with natural sort order."
    )
    parser.add_argument(
        "base_dir",
        type=Path,
        help="Path to the base directory containing the files."
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Starting number for sequential file naming."
    )

    args = parser.parse_args()
    rename_sequentially(args.base_dir, args.start)
