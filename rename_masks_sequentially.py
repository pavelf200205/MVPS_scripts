import os
import argparse
from natsort import natsorted

def rename_masks(folder_path):
	# Supported image extensions
	valid_extensions = ('.jpg', '.jpeg', '.jfif', '.JPG', '.JPEG', '.JFIF', '.png', '.PNG', '.webp', '.WEBP')

	# Get the list of the masks files
	files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(valid_extensions)]

	# Sort the masks files
	files = natsorted(files)

	# Rename each mask sequentially
	for index, filename in enumerate(files):
		# Get the file extension
		file_extension = os.path.splitext(filename)[1]

		# Create the new filename with a sequential number
		new_filename = f"{index:02}_mask{file_extension}"

		# Define the full paths for the old and new filenames
		old_filepath = os.path.join(folder_path, filename)
		new_filepath = os.path.join(folder_path, new_filename)

		# Rename the file
		os.rename(old_filepath, new_filepath)
		print(f"Ranamed: {old_filepath} to {new_filepath}")
	print("Renamed all images")

 
if __name__ == "__main__":
	# Set up argument parsing
	parser = argparse.ArgumentParser(description="Rename the image files sequentially in a folder.")
	parser.add_argument("folder_path", type=str, help="The path to the folder containing the image files.")

	# Parse the arguments
	args = parser.parse_args()

	# Rename the images sequentially in a specified folder
	rename_masks(args.folder_path)