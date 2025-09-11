import argparse
from pathlib import Path


def create_folders(parent_dir: Path, n: int, start: int):
    if not parent_dir.exists():
        print(f"The specified directory {parent_dir} does not exist.")
        return

    for i in range(start, start + n):
        folder_name = f"view_{i:02d}.data"
        folder_path = parent_dir / folder_name

        if not folder_path.exists():
            folder_path.mkdir(parents=True)
            print(f"Created folder: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create sequentially numbered folders.")
    parser.add_argument("parent_directory", type=Path, help="Path to the parent directory.")
    parser.add_argument("num_folders", type=int, help="Number of folders to create.")
    parser.add_argument("--start", type=int, default=0, help="Starting index for folder numbering (default: 0)")

    args = parser.parse_args()

    create_folders(args.parent_directory, args.num_folders, args.start)
