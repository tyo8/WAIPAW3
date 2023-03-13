import os
import sys
import csv
import h5py
import logging
import datetime
import numpy as np
import pandas as pd
import nibabel as nib
from sklearn.metrics import pairwise_distances
import collections
from collections import Counter
import warnings
import csv

warnings.filterwarnings('ignore')
nib.imageglobals.logger.setLevel(40)


def pull_subj_data(subject_id,
                   sub_cort_start_idx=59412,
                   find_subj_path='/scratch/tyoeasley/brain_representations/check_subj.sh',
                   outpath_type='/scratch/tyoeasley/brain_representations/gradient_reps/grad_maps/%s_subj-%s.npy'):
    print('\nStep 1: Load data and remove subcortical/cerebellar structrues')
    print(str(datetime.datetime.now()))
    outpath = outpath_type % ('%s', subject_id)

    # call bash script to find subject's filepath from subjID, read in filepath, and remove trailing newline '\n'
    # from string
    # fmri_fpath = os.popen(find_subj_path + ' ' + subject_id).read()[:-1]
    path = "/Users/yuanyuanxiaowang/Desktop/ukb/sub-1061708/ses-01/sub-1061708_ses-01_melodic.ica"

    data_list = [None] * 1
    session_id = 'filtered_func_data_clean_MNI152.nii.gz'
    # read in data
    # cifti_data = nib.load(fmri_fpath.replace('REST1_LR', session_id))
    nifti_data = nib.load(os.path.join(path, session_id))
    # cifti_headers = [cifti_data.header, cifti_data.nifti_header]
    nifti_headers = [nifti_data.header]
    data = nifti_data.get_fdata()

    # remove sub-cortical data
    # data = np.delete(data, range(sub_cort_start_idx, data.shape[1]), axis=1)

    data_list[0] = data

    return data_list, outpath, nifti_headers


subject_id = '200'
find_subj_path = '/Users/yuanyuanxiaowang/Desktop/check_subj.sh'
fmri_fpath = os.popen(find_subj_path + ' ' + subject_id).read()[:-1]

cifti_data = nib.load('/Users/yuanyuanxiaowang/Desktop/hcp/Results/rfMRI_REST1_LR_Atlas_hp2000_clean.dtseries.nii')
cifti_headers = [cifti_data.header, cifti_data.nifti_header]
data = cifti_data.get_fdata()

data = nib.load(
    "/Users/yuanyuanxiaowang/Desktop/ukb/sub-1061708/ses-01/sub-1061708_ses-01_melodic.ica/filtered_func_data_clean_MNI152.nii.gz")
data.shape
# (91, 109, 91, 490)
data_hdr = data.header
print(data.header)
data_hdr['pixdim']
ukb_data = data.get_fdata()
type(ukb_data)

mask = nib.load(
    "/Users/yuanyuanxiaowang/Desktop/ukb/sub-1061708/ses-01/sub-1061708_ses-01_melodic.ica/mask.nii.gz")
# (88, 88, 64)
mask_data = mask.get_fdata()
np.histogram(mask_data[mask_data != 0])
dd = collections.Counter(mask_data)




data = nib.load(
    "/Users/yuanyuanxiaowang/Desktop/ukb/sub-1061708/ses-01/sub-1061708_ses-01_melodic.ica/example_func.nii.gz")
# (88, 88, 64)
data = nib.load(
    "/Users/yuanyuanxiaowang/Desktop/ukb/sub-1061708/ses-01/sub-1061708_ses-01_melodic.ica/filtered_func_data_clean.nii.gz")
# (88, 88, 64, 490)
data = nib.load(
    "/Users/yuanyuanxiaowang/Desktop/ukb/sub-1061708/ses-01/sub-1061708_ses-01_melodic.ica/mean_func.nii.gz")
# (88, 88, 64)



fname = '/Users/yuanyuanxiaowang/Desktop/ukb/avg152T1_gray.img'
img = nib.load(fname)
nib.save(img, fname.replace('.img', '.nii'))

# example code for computing the nonzero overlap between mask and subject to check for consistency:
mask = nib.load('/Users/yuanyuanxiaowang/Desktop/ukb/final_GM_mask.nii.gz')
mask_data = mask.get_fdata()
mask_nzidx = set(np.nonzero(mask_data.flatten())[0])

root_path = "/Users/yuanyuanxiaowang/PycharmProjects/pythonProject/size_145_wapiaw"
path_list = ['F0_eid_wapiaw', 'F10_eid_wapiaw', 'F17_eid_wapiaw', 'F32_eid_wapiaw', 'F41_eid_wapiaw', 'G2_eid_wapiaw',
             'G8_eid_wapiaw', 'G35_37_eid_wapiaw', 'G40_eid_wapiaw', 'G43_eid_wapiaw', 'G45_eid_wapiaw',
             'G47_eid_wapiaw', 'G55_eid_wapiaw', 'G56_eid_wapiaw', 'G57_eid_wapiaw', 'G62_eid_wapiaw', 'G93_eid_wapiaw']
df_all_sbj = pd.DataFrame()
for filename in path_list:
    path = os.path.join(root_path, filename)
    df_all_sbj = df_all_sbj.append(pd.read_csv(path, index_col=0, header=0, dtype=str,names=['eid']))

df_all_sbj.to_csv("all_sbj.csv")

all_subj = df_all_sbj.values.tolist()
consistency = [None] * len(df_all_sbj)
for i,subj in enumerate(all_subj):
    path_part1 = "sub"+"-"+subj
    path_part2 = "sub"+'-'+subj+"_ses-01_melodic.ica"
    load_path = "/ceph/biobank/derivatives/melodic/"+ path_part1 +"/ses-01/"+path_part2+"/filtered_func_data_clean_MNI152.nii.gz"
    ukb_subj = nib.load(load_path)
    ukb_subj_data = ukb_subj.get_fdata()
    subj_nzidx = set(np.nonzero(ukb_subj_data.flatten())[0])
    consistency[i] = len(mask_nzidx.intersection(subj_nzidx)) / len(mask_nzidx)



# here's a fake but maybe somewhat helpful-ish approximation of what it will look to use the MNI mask for pulling & reshaping per-subject data:
mask = nib.load(<path to mask>      # should end up being an array of shape (91, 109, 91)
ukb_subj_data = *** do stuff to load subject data ***   # this should be of shape (91, 109, 91, T), where T is time (and i assume T=490 for all subjects?)
T = ukb_subj_data.shape(-1)
masked_ukb_subj_data = np.zeros((len(np.nonzero(mask)), T))
for t in T:
    volumetric_timeslice = ukb_subj_data[:,:,:,t]
    masked_ukb_subj_data[:,t] = volumetric_timeslice[mask]