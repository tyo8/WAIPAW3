import os
import sys
import csv
import argparse
import numpy as np

def_input_dir = "/scratch/tyoeasley/WAPIAW3/brainrep_data/ICA_data/dual_regression/example/ica25/groupICA25.dr" 
def_group_path = "/scratch/tyoeasley/WAPIAW3/subject_lists/combined_subj_eid/example.csv"

def extract_ICA_feats(input_dir=def_input_dir, dim=25, subjID_path=def_group_path, do_partial=True):
    print("extracting features from data in paths of form: ", input_dir)

    with open(subjID_path, newline='') as fin:
        subjID_list = list(map(''.join, list(csv.reader(fin))))

    outpath_gentype = os.path.join(os.path.dirname( input_dir ), "%s", "sub-")
    print("sending extracted features to paths of form: ", outpath_gentype % "FEATURE")

    for sID in subjID_list:
        fpath = os.path.join(input_dir, "dr_stage1_" + sID + ".txt")
        outpath_type = outpath_gentype + sID + '.csv'
        feats_from_dtseries(fpath, outpath_type, do_partial=True, dim=dim)


def feats_from_dtseries(fpath, outpath_type, do_partial=True, dim=300):
    ts_data = np.loadtxt(fpath)

    if ts_data.shape[1] != dim:
        print("Initial shape of given data (ICA_dim="+str(dim)+"): ", ts_data.shape)
        ts_data = ts_data.T
        assert ts_data.shape[1]==dim, "data dimension ("+str(ts_data.shape[1])+") does not match ICA dimension: " + str(dim)

    amps = np.std(ts_data, axis=1)
    netmats = np.corrcoef(ts_data)

    if do_partial:
        partial_netmats = _comp_partial_netmats(ts_data)
        # compute partial correlation matrix of ts_data

    write_out(outpath_type % 'Amplitudes', amps)
    write_out(outpath_type % 'NetMats', netmats)
    if do_partial:
        partial_netmats
        write_out(outpath_type % 'partial_NMs', partial_netmats)


def _comp_partial_netmats(data):
    C = np.cov(data)
    pcorr = np.linalg.pinv(C, hermitian=True)
    return pcorr



def write_out(outpath, data):
    savedir = os.path.dirname(os.path.abspath(outpath))
    if not os.path.isdir(savedir):
        os.makedirs(savedir)
    
    np.savetxt(outpath, data)


if __name__=="__main__":
    parser = argparse.ArgumentParser(
            description="Extract network matrices, partial network matrices, and amplitudes from ICA (dr_stage1) timeseries data (per subject)"
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
            help="dimension of decomposition (i.e., number of independent components computed from scan data)"
            )
    parser.add_argument(
            "-g", 
            "--group", 
            type=str, 
            default=def_group_path,
            help="filepath to list of subject ID numbers that compose subject group (and its corresponding matched controls)"
            )
    args=parser.parse_args()

    extract_ICA_feats(input_dir=args.input_dir, dim=args.dim, subjID_path=args.group)
