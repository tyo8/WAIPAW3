import os
import sys
import numpy as np
import pandas as pd 

def check_subj_list(subj_list_fpath):
    # 'all_sbj.csv' is a 1-column file with newline separators between (numeric ID) entries
    df_all_subj = pd.read_csv(subj_list_fpath, index_col=0, header=0, dtype=str)
    all_subj = df_all_subj.values.tolist()

    DNE_outname = "data_does_not_exist.txt"
    MNI_outname = "needs_MNI_registration.txt"

    for subj in all_subj:
        sID = subj[0]
        melodic_dir = "/ceph/biobank/derivatives/melodic"
        subj_dir = os.path.join(melodic_dir, f"sub-{sID}", "ses-01", f"sub-{sID}_ses-01_melodic.ica")
        if not os.path.isdir(subj_dir):
            with open(DNE_outname, 'a') as fout:
                fout.write(subj_dir + '\n')
                continue

        fname_type = "filtered_func_data_clean_MNI152.nii.gz"
        load_path = os.path.join(subj_dir, fname_type)
        if not os.path.isfile(load_path):
            new_fname_type = "filtered_func_data_clean.nii.gz"
            load_new_path = os.path.join(subj_dir, new_fname_type)
            if os.path.isfile(load_new_fpath):
                with open(MNI_outname, 'a') as fout:
                    fout.write(load_new_path + '\n')
            else:
                with open(DNE_outname, 'a') as fout:
                    fout.write(load_new_path + '\n')


if __name__=="__main__":
    if len(sys.argv) > 1:
        subj_list_fpath = sys.argv[1]
    else:
        subj_list_fpath = "/scratch/tyoeasley/WAPIAW3/subject_lists/all_sbj.csv"

    check_subj_list(subj_list_fpath)
