import os
import subprocess
import shutil
import argparse
from natsort import natsorted


def process_and_copy_images(mask_folder, views_folder):
	# Get the list of mask image files in the mask folder
	mask_files = [f for f in os.listdir(mask_folder) if os.path.isfile(os.path.join(mask_folder, f)) and f.endswith('.png')]

	# Sort the mask files to maintain order
	mask_files = natsorted(mask_files)

	for mask_file in mask_files:
		# Get the base name (without extension) to match with corresponding view folder
		base_name = os.path.splitext(mask_file)[0]
		mask_path = os.path.join(mask_folder, mask_file)

		# Define the destination subfolder in the views folder
		view_subfolder = os.path.join(views_folder, f"view_{base_name}.data")

		if not os.path.exists(view_subfolder):
			print(f"View subfolder {view_subfolder} does not exist. Skipping {mask_file}.")

		# Process the image (crop and resize) with ImageMagick
		try:
			# Copy the cropped and resized mask image to the corresponding view subfolder
			destination_path = os.path.join(view_subfolder, "mask.png")
			shutil.copy(mask_path, destination_path)
			print(f"Copied {mask_file} to {destination_path} as mask.png")

		except Exception as e:
			print(f"An unexpected error occured: {e}")

	print("All mask images have been processed and copied")


if __name__ == "__main__":
	# Set up argument parsing
	parser = argparse.ArgumentParser(description="Crop, resize mask images and copy them to corresponding view subfolders.")
	parser.add_argument("mask_folder", type=str, help="The path to the mask folder containing the image files")
	parser.add_argument("views_folder", type=str, help="The path to the views folder containing the view subfolders")

	# Parse the arguments
	args = parser.parse_args()

	# Process and copy the images
	process_and_copy_images(args.mask_folder, args.views_folder)