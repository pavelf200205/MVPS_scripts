import os
import argparse
import subprocess

def load_camera_params(cameras_txt_path):
    """
    Load camera intrinsics from a COLMAP cameras.txt file.
    It skips comments and the "Number of cameras:" line and returns the camera parameters string.
    For example, from
    1 PINHOLE 835 1121 871.97443405134527 871.97443405134527 417.5 560.5
    It returns:
      "PINHOLE 835 1121 871.97443405134527 871.97443405134527 417.5 560.5"
    """
    with open(cameras_txt_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comment lines and the "Number of cameras:" line.
            if line.startswith("#"):
                continue
            parts = line.split()
            # Skip the first part (camera id) and join the rest
            camera_params = " ".join(parts[1:])
            return camera_params
    return None


def process_subfolders(all_mvps_images_path, undistorted_mvps_images_path, camera_params):
    """
    For each subfolder in the given MVPS views directory:
    1. Create an undistortion.txt file with a line per JPEG image in the folder.
    2. Run the COLMAP image undistorted standalone command.
    """

    # Iterate over each subfolder
    for subfolder in os.listdir(all_mvps_images_path):
        subfolder_path = os.path.join(all_mvps_images_path, subfolder)
        if os.path.isdir(subfolder_path):
            # List all .jpg files (case insensitive) in the subfolder
            image_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith(('.jpg', '.jpeg'))]

            # Write the undistortion.txt file.
            undistortion_file_path = os.path.join(subfolder_path, "undistortion.txt")
            with open(undistortion_file_path, 'w') as out_file:
                for image in image_files:
                    out_file.write(f"{image} {camera_params}\n")
                out_file.write(f"mask.png {camera_params}")
            
            # Ensure the output directory for undistorted images exists.
            undistorted_subfolder_path = os.path.join(undistorted_mvps_images_path, subfolder)
            os.makedirs(undistorted_subfolder_path, exist_ok=True)

            # Build the COLMAP command.
            cmd = [
                "colmap", "image_undistorter_standalone",
                "--image_path", subfolder_path,
                "--input_file", undistortion_file_path,
                "--output_path", undistorted_subfolder_path
            ]

            # Run the command.
            subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Undistort all MVPS images."
    )
    parser.add_argument("--cameras_txt_path", required=True,
                        help="Path to the cameras.txt file")
    parser.add_argument("--all_mvps_images_path", required=True,
                        help="Path to the folder containing MVPS views")
    parser.add_argument("--undistorted_mvps_images_path", required=True,
                        help="Path to save the undistorted MVPS images")
    args = parser.parse_args()

    camera_params = load_camera_params(args.cameras_txt_path)
    if camera_params is None:
        print("Error: No camera parameters found in", args.camera_txt_path)
        return
    
    process_subfolders(args.all_mvps_images_path, args.undistorted_mvps_images_path, camera_params)


if __name__ == "__main__":
    main()