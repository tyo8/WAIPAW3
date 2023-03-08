import os
import numpy as np
import pandas as pd
import nibabel as nib
import collections
from collections import Counter
import warnings
import csv

warnings.filterwarnings('ignore')
nib.imageglobals.logger.setLevel(40)

mask = nib.load('final_GM_mask.nii.gz')
mask_data = mask.get_fdata()
mask_nzidx = set(np.nonzero(mask_data.flatten())[0])

# 'all_sbj.csv' is a 1-column file with newline separators between (numeric ID) entries:q
df_all_subj = pd.read_csv("all_sbj.csv", index_col=0, header=0, dtype=str)
all_subj = df_all_subj.values.tolist()

consistency = [None] * len(all_sbj)

for i, subj in enumerate(all_subj):
    sID = subj[0]
    melodic_dir = "/ceph/biobank/derivatives/melodic"
    fname_type = "filtered_func_data_clean_MNI152.nii.gz"
    load_path = os.path.join(melodic_dir, f"sub-{sID}", "ses-01", f"sub-{sID}_ses-01_melodic", fname_type)
    os.popen(f"test -f {load_path} || echo {load_path} >> does_not_exist.csv")
