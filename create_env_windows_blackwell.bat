conda deactivate
conda remove -y -n sn --all
conda create -y -n sn python=3.10
conda activate sn

python -m pip install pip==25.2
pip install torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu129

rem Install pyembree first so that it downgrades the 'setuptools'
rem and 'wheel' so 'nerfacc' installation doesn't fail.
rem pip install setuptools==60.10.0 wheel==0.37.1
pip install pyembree==0.1.12

pip install -e ./third_parties/nerfacc-0.3.5/nerfacc-0.3.5/

pip install git+https://github.com/NVlabs/tiny-cuda-nn/@2ec562e853e6f482b5d09168705205f46358fb39#subdirectory=bindings/torch

pip install tqdm==4.67.1 opencv-python==4.8.1.78 trimesh==3.23.5 open3d==0.17 pyvista==0.46.3 scipy==1.10.1 scikit-image==0.21.0 pyhocon==0.3.59 pyexr==0.3.10 tensorboard==2.14.0 icecream==2.1.3 PyMCubes==0.1.4
