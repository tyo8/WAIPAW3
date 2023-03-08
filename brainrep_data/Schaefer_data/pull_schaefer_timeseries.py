import os
import sys
import argparser
import numpy as np
import nibabel as nib


def_datapath_type="/ceph/biobank/derivatives/melodic/sub-%s/ses-01/sub-%s_ses-01_melodic.ica/filtered_func_data_clean_MNI152.nii.gz"
def_parcelpath_type="/scratch/tyoeasley/WAPIAW3/brainrep_data/Schaefer_data/parcellation_defs/MNI/Schaefer2018_%sParcels_%sNetworks_order_FSLMNI152_%smm.nii.gz"
def_outpath_type="/scratch/tyoeasley/WAPIAW3/brainrep_data/Schaefer_data/timeseries/sub-%s.txt"
def_group_path="/scratch/tyoeasley/WAPIAW3/subject_lists/all_subj.csv"

def pull_and_save_schaefer_ts(
        datapath_type=def_datapath_type, 
        parcelpath_type=def_parcelpath_type,
        outpath_type=def_outpath_type,
        group_path=def_group_path,
        dim=400, 
        networks=17, 
        mm_res=2
        ):

    parcelpath = parcelpath_type % (dim, networks, mm_res)
    parcellation = nib.load(parcelpath).get_fdata()

    with open(group_path, 'r') as fin:
        subjID_list = fin.read().split()

    for subjID in subjID_list:
        img_data = nib.load( outpath_type % (subjID, subjID) ).get_fdata()
        ts_data = comp_avg_ts(img_data, parcellation, dim=dim)
        
        outpath = outpath_type % subjID
        np.savetxt(outpath, ts_data)



def comp_avg_ts(raw_data, parcellation, dim=400):
    ts_data = np.asarray([[np.mean(
            np.rollaxis(raw_data, -1)[i][parcellation == j])
            for i in range(data.shape[-1])] 
            for j in range(1,dim+1)])
    return ts_data


if __name__=="__main__":
    parser = argparse.ArgumentParser(
            description="Extracts average per-parcel timeseries from raw rfMRI data according to (the user-specified version of) the Schaefer parcellation"
            )
    parser.add_argument(
            "-i",
            "--input_datapath_type",
            type=str,
            default=def_datapath_type,
            help="Generalized path to input data; substitutes subject eid via printf to specify readpath to raw data."
            )
    parser.add_argument(
            "-o",
            "--outpath_type",
            type=str,
            default=def_outpath_type,
            help="Generalized path to output data; substitutes subject eid via printf to specify savepath to timeseries data."
            )
    parser.add_argument(
            "-o",
            "--parcelpath_type",
            type=str,
            default=def_parcelpath_type,
            help="Generalized path to parcellation definition; substitutes dimension, network number, and mm resolution to specify path to definition."
            )
    parser.add_argument(
            "-g",
            "--group",
            type=str,
            default=def_group_path,
            help="filepath to list of subject ID numbers that compose subject group (and its corresponding matched controls)"
            )
    parser.add_argument(
            "-d",
            "--dim",
            type=int,
            default=400,
            help="dimension of decomposition (i.e., number of Schaefer parcels)"
            )
    parser.add_argument(
            "-n",
            "--networks",
            type=int,
            default=17,
            help="number of Yeo networks defined in parcellation; parametrizes parcellation choice (either 7 or 17)"
            )
    parser.add_argument(
            "-r",
            "--res",
            type=int,
            default=2,
            help="(isotropic) spatial resolution, in mm; parametrizes parcellation choice"
            )
    args=parser.parse_args()
    assert args.networks == 17 | args.networks == 7, "invalid number of Yeo networks specified"
    
    pull_and_save_schaefer_ts(
        datapath_type=args.input_datapath_type,
        parcelpath_type=args.parcelpath_type,
        outpath_type=args.outpath_type
        group_path=args.group_path,
        dim=args.dim, 
        networks=args.networks, 
        mm_res=args.res
        )
