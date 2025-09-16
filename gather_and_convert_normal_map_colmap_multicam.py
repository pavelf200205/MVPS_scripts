import os
import pyexr
import numpy as np
import shutil
import argparse

def make4x4(P):
    assert P.shape[-1] == 4 or P.shape[-1] == 3
    assert len(P.shape) == 2
    assert P.shape[0] == 3 or P.shape[0] == 4
    ret = np.eye(4)
    ret[:P.shape[0], :P.shape[1]] = P
    return ret


def quaternion_to_rotation_matrix(qw, qx, qy, qz):
    R = np.array([
       [1 - 2*qy**2 - 2*qz**2, 2*qx*qy - 2*qz*qw, 2*qx*qz + 2*qy*qw],
       [2*qx*qy + 2*qz*qw, 1 - 2*qx**2 - 2*qz**2, 2*qy*qz - 2*qx*qw],
       [2*qx*qz - 2*qy*qw, 2*qy*qz + 2*qx*qw, 1 - 2*qx**2 - 2*qy**2]
    ])
    return R


parser = argparse.ArgumentParser()
parser.add_argument("--colmap_path", type=str, required=True)
parser.add_argument("--sdm_unips_result_dir", type=str, required=True)
parser.add_argument("--data_dir", type=str, required=True)
args = parser.parse_args()


# Create file paths
cameras_txt_path = os.path.join(args.colmap_path, "cameras.txt")
images_txt_path = os.path.join(args.colmap_path, "images.txt")

# Load camera intrinsics from cameras.txt
with open(cameras_txt_path, 'r') as f:
    camera_lines = [line.strip() for line in f if not line.startswith('#') and line.strip()]
camera_data = camera_lines[0].split()

# Focal distance and principal point
fx, fy, cx, cy = map(float, camera_data[4:8])

# Camera matrix
K = np.array([[fx, 0, cx],
              [0, fy, cy], 
              [0, 0, 1]])


# Load camera extrinsics from images.txt (World-to-Camera transforms)
with open(images_txt_path, 'r') as f:
    image_lines = [line.strip() for line in f if not line.startswith('#') and line.strip()]

# Remove every second line from image_lines (skip the 2D points for each image)
image_lines = image_lines[::2]

# Create directories for gathered and converted normal maps in the data_dir
normal_map_camera_dir = os.path.join(args.data_dir, "normal_camera_space_sdmunips")
normal_map_world_dir = os.path.join(args.data_dir, "normal_world_space_sdmunips")
os.makedirs(normal_map_camera_dir, exist_ok=True)
os.makedirs(normal_map_world_dir, exist_ok=True)

# Create a list of W2C transforms from colmap model
W2C_list = []
for line in image_lines:
    image_data = line.split() # IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME
    qw, qx, qy, qz = map(float, image_data[1:5])
    tx, ty, tz = map(float, image_data[5:8])
    filename = image_data[-1]
    view_id = os.path.splitext(filename)[0]
    R = quaternion_to_rotation_matrix(qw, qx, qy, qz)
    t = np.array([tx, ty, tz]).reshape([3, 1])
    
    W2C = np.zeros((4, 4))
    W2C[3, 3] = 1
    W2C[:3, :3] = R
    W2C[:3, [3]] = t

    # Get the Camera-to-World transform from World-to-Camera transform
    C2W = np.linalg.inv(W2C)
    # Get the rotation matrix from Camera-to-World transform
    R = C2W[:3, :3]

    # Get the name of subfolder in the results folder for the current view
    view_dir = os.path.join(args.sdm_unips_result_dir, f"view_{view_id}.data")
    
    # Copy the normal map from subfolder to normal_camera_space_sdmunips dir
    normal_map_file = os.path.join(view_dir, "normal.exr")
    new_normal_map_file = os.path.join(normal_map_camera_dir, f"{view_id}.exr")
    shutil.copy(normal_map_file, new_normal_map_file)

    # Convert the normal map to world space
    normal_map_camera = pyexr.read(new_normal_map_file)
    normal_map_camera[..., [1, 2]] *= -1 # revert y and z axis to match opencv conversion, X right, Y down, Z front
    H, W = normal_map_camera.shape[:2]
    normal_world = (R @ normal_map_camera.reshape(-1, 3).T).T.reshape([H, W, 3])

    # Save the world space normal map
    normal_map_world_file = os.path.join(normal_map_world_dir, f"{view_id}.exr")
    pyexr.write(normal_map_world_file, normal_world) 
