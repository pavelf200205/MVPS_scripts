import os
import subprocess
import argparse


def crop_and_resize(folder_path, crop_ROI, resized_size):
	# Get the list of subfolders in the parent folder
	subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

	for subfolder in subfolders:
		subfolder_path = os.path.join(folder_path, subfolder)

		try:
			# Construct the ImageMagick commands
			# crop_command = ['mogrify', '-crop', '3008x3008+504+0', '*.jpg']
			# resize_command = ['mogrify', '-crop', '2560x2560+728+224', '-resize', '1024x1024', '-quality', '100', '*.jpg']
			command = ['mogrify', '-crop', crop_ROI, '-resize', resized_size, '-quality', '100', '*.jpg']
			# # Run the crop command in the current subfolder
			# subprocess.run(crop_command, shell=True, cwd=subfolder_path, check=True)
			# print(f"Cropped the images in the directory: {subfolder_path}")

			# Run the resize command in the current subfolder
			subprocess.run(command, shell=True, cwd=subfolder_path, check=True)
			print(f"Resized the images in the directory: {subfolder_path}")

		except Exception as e:
			print(f"An error occured in folder {subfolder_path}: {e}")
			
	print("Cropped and resized all images.")


if __name__ == "__main__":
	# Set up argument parsing
	parser = argparse.ArgumentParser(description="Crop and resize the jpg images in the subfolders of a given folder")
	parser.add_argument("folder_path", type=str, help="The path to the folder containing the image subfolders")
	parser.add_argument("crop_ROI", type=str)
	parser.add_argument("resized_size", type=str)
	# Parse the arguments
	args = vars(parser.parse_args())

	# Crop and resize the images in each subfolder
	crop_and_resize(**args)