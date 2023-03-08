import os
import sys
import csv
import argparse
import numpy as np

def_input_dir = "/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/out_PROFUMO/d25_example.pfm/%s" 
def_group_path = "/scratch/tyoeasley/WAPIAW3/subject_lists/combined_subj_eid/example.csv"

def extract_PROFUMO_feats(input_dir=def_input_dir, dim=25, subjID_path=def_group_path):
    print("extracting features from data in paths of form: ", input_dir)

    with open(subjID_path, newline='') as fin:
        subjID_list = list(map(''.join, list(csv.reader(fin))))

    inpath_gentype = os.path.join(input_dir % "Maps","sub-sub-%s.csv")
    outpath_gentype = os.path.join(input_dir,"sub-%s.csv")
    print("sending extracted features to paths of form: ", outpath_gentype % ("<FEATURE>","<eid>"))

    for sID in subjID_list:
        inpath = inpath_gentype % sID
        outpath_type = outpath_gentype % ("%s", sID)
        feats_from_dtseries(inpath, outpath_type, dim=dim)


def feats_from_dtseries(fpath, outpath_type, dim=300):
    map_data = np.loadtxt(fpath)

    if map_data.shape[1] != dim:
        print("Initial shape of given data (PROFUMO_dim="+str(dim)+"): ", map_data.shape)
        map_data = map_data.T
        assert map_data.shape[1]==dim, "data dimension ("+str(map_data.shape[1])+") does not match PROFUMO dimension: " + str(dim)

    netmats = np.corrcoef(map_data)

    write_out(outpath_type % 'spNMs', netmats)

def write_out(outpath, data):
    savedir = os.path.dirname(os.path.abspath(outpath))
    if not os.path.isdir(savedir):
        os.makedirs(savedir)
    
    np.savetxt(outpath, data)


if __name__=="__main__":
    parser = argparse.ArgumentParser(
            description="Extract network matrices, partial network matrices, and amplitudes from PROFUMO (dr_stage1) timeseries data (per subject)"
            )
    parser.add_argument(
            "-i", 
            "--input_dir", 
            type=str, 
            default=def_input_dir,
            help="Path to input data; substitutes subject eid via printf to specify filepath to timeseries data."
            )
    parser.add_argument(
            "-d", 
            "--dim", 
            type=int, 
            default=25,
            help="dimension of decomposition (i.e., number of probabilistic functional modes computed from scan data)"
            )
    parser.add_argument(
            "-g", 
            "--group", 
            type=str, 
            default=def_group_path,
            help="filepath to list of subject ID numbers that compose subject group (and its corresponding matched controls)"
            )
    args=parser.parse_args()

    extract_PROFUMO_feats(input_dir=args.input_dir, dim=args.dim, subjID_path=args.group)
