import argparse
import subprocess
import shutil
from pathlib import Path


def process_subfolders(parent_folder: Path, target_folder: Path, mode: str):
    # Create target folder if it doesn't exist
    target_folder.mkdir(parents=True, exist_ok=True)

    # Loop through subfolders
    for subfolder in parent_folder.iterdir():
        if subfolder.is_dir():
            try:
                jpg_files = list(subfolder.glob("*.jpg"))
                if not jpg_files:
                    print(f"Skipping {subfolder} (no .jpg files found)\n")
                    continue

                print(f"Processing folder: {subfolder}\n")

                # Construct ImageMagick command
                command = [
                    "convert",
                    "*.jpg",
                    "-evaluate-sequence", mode,
                    "stacked.jpg"
                ]

                # Run in the subfolder's directory
                subprocess.run(command, shell=True, cwd=subfolder, check=True)

                # Rename stacked.jpg → {subfolder_name}.jpg
                old_path = subfolder / "stacked.jpg"
                new_filename = f"{subfolder.stem}.jpg"
                new_path = subfolder / new_filename
                old_path.rename(new_path)

                # Move to target folder
                shutil.move(str(new_path), target_folder / new_filename)
                print(f"Moved {new_filename} to {target_folder}\n")

            except Exception as e:
                print(f"An error occurred in folder {subfolder}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stack JPGs in each subfolder using ImageMagick.")
    parser.add_argument("parent_folder", type=Path, help="Path to the parent folder containing subfolders.")
    parser.add_argument("target_folder", type=Path, help="Path to the folder where results will be stored.")
    parser.add_argument("--mode", type=str, default="max",
                        help="ImageMagick evaluate-sequence mode (e.g., max, mean, min). Default: max")

    args = parser.parse_args()

    process_subfolders(args.parent_folder, args.target_folder, args.mode)
