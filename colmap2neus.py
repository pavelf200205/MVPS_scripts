import os.path
import xml

import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# details of camera normalization can be found in Sec. C.3 in https://openaccess.thecvf.com/content/CVPR2023/supplemental/Cao_Multi-View_Azimuth_Stereo_CVPR_2023_supplemental.pdf
def normalize_camera(R_list, t_list, camera2object_ratio=3):
    A_camera_normalize = 0
    b_camera_normalize = 0
    camera_center_list = []
    for view_idx in range(len(R_list)):
        R = R_list[view_idx]
        t = t_list[view_idx]
        camera_center = - R.T @ t  # in world coordinate
        camera_center_list.append(camera_center)
        vi = R[2][:, None]  # the camera's principal axis in the world coordinates
        Vi = vi @ vi.T
        A_camera_normalize += np.eye(3) - Vi
        b_camera_normalize += camera_center.T @ (np.eye(3) - Vi)
    offset = np.linalg.lstsq(A_camera_normalize, np.squeeze(b_camera_normalize), rcond=None)[0]
    camera_center_dist_list = [np.sqrt(np.sum((np.squeeze(c) - offset) ** 2))
                               for c in camera_center_list]
    scale = np.max(camera_center_dist_list) / camera2object_ratio
    return offset, scale

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

class ColmapPoseLoader:
    def __init__(self, model_path, camera2object_ratio):
        # Create file paths
        cameras_txt_path = os.path.join(model_path, "cameras.txt")
        images_txt_path = os.path.join(model_path, "images.txt")

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
        
        # Load camera extrinsics from images.txt
        with open(images_txt_path, 'r') as f:
            image_lines = [line.strip() for line in f if not line.startswith('#') and line.strip()]

        # Remove every second line from image_lines (skip the 2D points for each image)
        image_lines = image_lines[::2]


        R_list = []
        t_list = []
        camera_sphere = {}
        for line in image_lines:
            image_data = line.split() # IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME
            qw, qx, qy, qz = map(float, image_data[1:5])
            tx, ty, tz = map(float, image_data[5:8])
            filename = image_data[-1]
            view_id = int(os.path.splitext(filename)[0])
            R = quaternion_to_rotation_matrix(qw, qx, qy, qz)
            t = np.array([tx, ty, tz]).reshape([3, 1])

            W2C = np.zeros((4, 4))
            W2C[3, 3] = 1
            W2C[:3, :3] = R
            W2C[:3, [3]] = t

            R_list.append(R)
            t_list.append(t)

            camera_sphere[f"world_mat_{view_id}"] = make4x4(K) @ W2C

        offset, scale = normalize_camera(R_list, t_list, camera2object_ratio=camera2object_ratio)
        print("offset", offset, "scale", scale)
        num_views = len(R_list)

        scale_mat = np.eye(4)
        scale_mat[:3, :3] *= scale
        scale_mat[:3, 3] = offset
        for im_idx in range(num_views):
            camera_sphere[f"scale_mat_{im_idx}"] = scale_mat
        np.savez(os.path.join(model_path, "cameras_sphere.npz"), **camera_sphere)


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--colmap_path", type=str, required=True, help="Path to the COLMAP model in TXT format (cameras.txt, images.txt, points3D.txt)")
    parser.add_argument("--ratio", type=float, default=10)
    args = parser.parse_args()

    ColmapPoseLoader(args.colmap_path, camera2object_ratio=args.ratio)