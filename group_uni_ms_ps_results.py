from pathlib import Path
import shutil
import argparse
from natsort import natsorted
import re

def group_inference_files(source_dir: Path, target_base_dir: Path):
    if not source_dir.exists():
        print(f"Source directory '{source_dir}' does not exist.")
        return

    target_base_dir.mkdir(parents=True, exist_ok=True)

    # Match files like view_00.data.exr or view_00.data.png
    pattern = re.compile(r"(view_\d+)\.data\.(exr|png)$")

    # Group files by view ID
    grouped_files = {}
    for file in source_dir.iterdir():
        if file.is_file():
            match = pattern.match(file.name)
            if match:
                view_id, ext = match.groups()
                grouped_files.setdefault(view_id, {})[ext] = file

    # Sort view IDs naturally
    for view_id in natsorted(grouped_files.keys()):
        subdir_path = target_base_dir / f"{view_id}.data"
        subdir_path.mkdir(parents=True, exist_ok=True)

        for ext, file_path in grouped_files[view_id].items():
            target_filename = f"normal.{ext}"
            shutil.copy2(file_path, subdir_path / target_filename)
            print(f"Copied {file_path.name} to {subdir_path} as '{target_filename}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Group Uni-MS-PS inference outputs into SDM-UniPS-style folders.")
    parser.add_argument("unimsps_inference_folder", type=Path, help="Path to the folder with estimated normal maps.")
    parser.add_argument("export_folder", type=Path, help="Path to the output folder.")
    args = parser.parse_args()

    group_inference_files(args.unimsps_inference_folder, args.export_folder)
