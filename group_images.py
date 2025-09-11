import os
import argparse
from natsort import natsorted
import shutil


def group_images(image_folder, parent_folder, group_size, start_id):
    # Get the list of image files and sort them in natural order
    images = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    sorted_images = natsorted(images)

    # Calculate number of subfolders needed
    num_subfolders = len(sorted_images)//group_size
    # Create subfolders and move images
    for i in range(start_id, num_subfolders+start_id):
        # Define the subfolder name
        subfolder_name = f"view_{i:02}.data"
        subfolder_path = os.path.join(parent_folder, subfolder_name)

        # Create the subfolder if it doesn't exist
        os.makedirs(subfolder_path, exist_ok=True)

        # Get the images for this subfolder
        start_idx = i * group_size
        end_idx = start_idx + group_size
        images_to_move = sorted_images[start_idx:end_idx]

        # Move each image to the subfolder
        for img in images_to_move:
            src_path = os.path.join(image_folder, img)
            dst_path = os.path.join(subfolder_path, img)
            shutil.move(src_path, dst_path)
        print(f"Moved images to {subfolder_path}")


if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Group images into subfolders.")
    parser.add_argument("image_folder", type=str, help="Directory where the image files are located")
    parser.add_argument("parent_folder", type=str, help="Parent directory where subfolders will be created")
    parser.add_argument("group_size", type=int, help="Number of images in each subfolder")
    parser.add_argument("--start_id", type=int, default=0, help="The start folder index")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function to group images
    group_images(args.image_folder, args.parent_folder, args.group_size, args.start_id)