import argparse
import os
import shutil
import sys
from pathlib import Path
from natsort import natsorted


def confirm(prompt, default=False):
	suffix = " [Y/n]: " if default else " [y/N] "
	reply = input(prompt + suffix).strip().lower()
	if not reply:
		return default
	return reply in ['y', 'yes']


def collect_images(dataset_path):
	allowed_exts = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".gif", ".webp", ".avif", ".jxl"}
	all_images = []
	camera_folders = natsorted([p for p in dataset_path.iterdir() if p.is_dir()])

	for folder in camera_folders:
		image_files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in allowed_exts]
		sorted_images = sorted(image_files)
		for image_path in sorted_images:
			rel_path = image_path.relative_to(dataset_path).as_posix().lower()
			all_images.append((rel_path, image_path))

	return all_images


def generate_digit_format(n):
	return max(2, len(str(n - 1)))


def flatten_images(image_list, output_folder, masks_folder=None):
	output_folder.mkdir(parents=True, exist_ok=True)
	if masks_folder:
		(output_folder / "masks").mkdir(parents=True, exist_ok=True)

	digit_count = generate_digit_format(len(image_list))
	mapping = {}

	for idx, (rel_path, full_path) in enumerate(image_list):
		ext = full_path.suffix.lower()
		new_name = f"{idx:0{digit_count}d}{ext}"
		dest_path = output_folder / new_name
		shutil.copy2(full_path, dest_path)
		mapping[rel_path] = new_name

		if masks_folder:
			mask_rel_path = rel_path + ".png"  # e.g., IMG.jpg -> IMG.jpg.png
			mask_path = masks_folder / mask_rel_path
			if mask_path.exists():
				# Strip image extension and append only .png
				mask_basename = Path(new_name).stem + ".png"
				mask_dest_path = output_folder / "masks" / mask_basename
				shutil.copy2(mask_path, mask_dest_path)
			else:
				print(f"[!] Warning: Mask not found for image '{rel_path}' at '{mask_path}'")

	return mapping


def update_images_txt(images_txt_path, mapping):
	output_file = images_txt_path.parent / "images_flat.txt"
	with open(images_txt_path, 'r') as f:
		lines = f.readlines()

	output_lines = []
	i = 0
	while i < len(lines):
		line = lines[i]
		if line.strip().startswith("#") or line.strip() == "":
			output_lines.append(line)
			i += 1
			continue

		parts = line.strip().split()
		if len(parts) >= 10:
			image_name = parts[-1].lower()
			if image_name in mapping:
				parts[-1] = mapping[image_name]
			else:
				print(f"Warning: '{image_name}' not found in mapping!")
			output_lines.append(" ".join(parts) + "\n")
			output_lines.append(lines[i + 1])  # second line: 2D keypoints
			i += 2
		else:
			output_lines.append(line)
			i += 1

	with open(output_file, 'w') as f:
		f.writelines(output_lines)

	print(f"[✓] Updated images.txt saved to: {output_file}")


def write_log(log_path, mapping):
	with open(log_path, 'w') as f:
		for orig, new in mapping.items():
			f.write(f"{orig} -> {new}\n")
	print(f"[✓] Mapping log saved to: {log_path}")


def main():
	parser = argparse.ArgumentParser(description="Flatten COLMAP rig dataset and update images.txt")
	parser.add_argument("rig_dataset", type=Path, help="Path to the rig dataset folder")
	parser.add_argument("images_txt", type=Path, help="Path to the original images.txt file")
	parser.add_argument("output_folder", type=Path, help="Path to store the flattened images")
	parser.add_argument("--masks_folder", type=Path, help="Path to the masks folder (same structure as rig dataset)")
	parser.add_argument("--log", type=Path, help="Path to save the file renaming log (mapping.txt)")

	args = parser.parse_args()

	if args.output_folder.exists():
		if not confirm(f"[!] Output folder '{args.output_folder}' already exists. Overwrite?", default=False):
			print("Aborted.")
			sys.exit(1)
		shutil.rmtree(args.output_folder)

	print(f"[i] Collecting images from: {args.rig_dataset}")
	image_list = collect_images(args.rig_dataset)
	print(f"[i] Found {len(image_list)} images.")

	print(f"[i] Flattening images into: {args.output_folder}")
	mapping = flatten_images(image_list, args.output_folder, args.masks_folder)

	print(f"[i] Updating images.txt from: {args.images_txt}")
	update_images_txt(args.images_txt, mapping)

	if args.log:
		print(f"[i] Saving log to: {args.log}")
		write_log(args.log, mapping)

	print("[✓] Done.")


if __name__ == "__main__":
	main()
