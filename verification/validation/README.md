# Exact-refraction benchmark reproduction

Use Python 3.12 (the recorded run used 3.12.14) and Node.js.
From this directory:

```sh
python -m pip install -r requirements.txt
node goil_matrix.cjs ../software_igolab/index.html
python validity.py
python compare_rayoptics.py
python check_results.py
```

Installing all RayOptics dependencies also installs its GUI stack. For just the routines used here, the recorded headless setup installed NumPy, SciPy and Matplotlib at the versions in requirements.txt, then `rayoptics==0.9.8 transforms3d==0.4.2` with `--no-deps`. The scripts use unmodified package routines; the full GUI is not needed.

`validity.py` uses its independently assembled paraxial matrix as the comparison prediction. `goil_matrix.cjs` extracts the actual GOIL matrix function; `check_results.py` asserts their numerical agreement. The exact reference and RayOptics routines are compared separately. The 4040 ray checks are NOT 4040 direct GOIL bench comparisons.

Lengths are cm. The bundle half-width is defined in the front vertex plane; it is not the surface semi-aperture. Each of 40 parameter combinations has 101 equal-weight meridional rays. The supplied CSV and JSON files are the recorded results and are overwritten by reproduction. The figure PDF is a vector export for publication. No renderer QA files are included.
