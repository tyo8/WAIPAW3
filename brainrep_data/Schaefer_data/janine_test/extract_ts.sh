#!/bin/bash

#SBATCH --job-name=extract_sanity_check
#SBATCH --time=23:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --mem=20gb


module load fsl

for s in `cat /scratch/tyoeasley/WAPIAW3/subject_lists/combined_subj_eid/rmed_G35_37_eid_wapiaw.csv` ; do
	echo ${s}
	fslmeants -i /ceph/biobank/derivatives/melodic/sub-${s}/ses-01/sub-${s}_ses-01_melodic.ica/filtered_func_data_clean_MNI152.nii.gz -o sub-${s}.txt --label=/scratch/tyoeasley/WAPIAW3/brainrep_data/Schaefer_data/parcellation_defs/MNI/Schaefer2018_400Parcels_17Networks_order_FSLMNI152_2mm.nii.gz
done
