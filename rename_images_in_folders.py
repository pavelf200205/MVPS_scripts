import os
import shutil
from natsort import natsorted
import argparse

def rename_images_in_subfolders(parent_folder):
	valid_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.jfif', '.JFIF')
	# Iterate through each subfolder in the parent folder
	for subdir, dirs, files in os.walk(parent_folder):
		# Filter only image files

		image_files = [f for f in files if f.endswith(valid_extensions)]

		# Sort the files alphabetically
		image_files.sort()

		# Rename each image file sequentially
		for index, filename in enumerate(image_files):
			# Create the new filename with a sequential number (padded with leading zeros)
			new_filename = f"L{index:02}.jpg"

			# Define the full patchs for the old and new filenames
			old_filepath = os.path.join(subdir, filename)
			new_filename = os.path.join(subdir, new_filename)

			# Rename the file
			os.rename(old_filepath, new_filename)
		print(f"Renamed all images in {subdir}")
	print("Renaming complete for all subfolders.")

if __name__ == "__main__":
	# Set up argument parsing
	parser = argparse.ArgumentParser(description="Rename all images in subfolders to L00, L01, ..., L99")
	parser.add_argument("folder_path", type=str, help="The path to the folder containing the image subfolders")
	# Parse the arguments
	args = parser.parse_args()

	rename_images_in_subfolders(args.folder_path)