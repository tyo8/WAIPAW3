import os
import sys
import csv
import numpy as np
import nibabel as nb

profumo_outdir = '/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/out_PROFUMO/rmed_G8_eid_wapiaw_25_Results.ppp'

def main(
        genpath = os.path.join(profumo_outdir,'Maps/'),
       # good_modes = np.sort([int(i) for i in np.genfromtxt(os.path.join(profumo_outdir, 'signal_components.txt'))]),
        subjID_path = '/scratch/tyoeasley/WAPIAW3/subject_lists/all_subj_eid.csv', 
        do_partial = True
        ):

    with open(subjID_path, newline='') as fin:
        subjID_list = list(map(''.join, list(csv.reader(fin))))

    genpath_in = genpath + 'sub-%s.dscalar.nii'
    #genpath_in = genpath + 'sub-%s.nii.gz'
    genpath_out = genpath + 'sub-%s_spNM.txt'

    for sID in subjID_list:
        try:
            fpath = genpath_in % sID
            ts_data = _load_data(fpath)
           # ts_data = ts_data[good_modes,:]
        except IOError:
            err_log = open('missing_subj_data.csv','a')
            err_log.write(fpath+'\n')
            err_log.close()
            continue
        # print(ts_data) 
        spNM = np.corrcoef(ts_data)
        
        outpath = genpath_out % sID
        write_out(outpath, spNM)



def _load_data(fpath):
    ts_data = nb.load(fpath).get_fdata()
    if ts_data.shape[0] > ts_data.shape[1]:
        ts_data = ts_data.T

    return ts_data


def write_out(outpath, data):
    savedir = os.path.dirname(os.path.abspath(outpath))
    if not os.path.isdir(savedir):
        os.makedirs(savedir)
    
    np.savetxt(outpath, data)


if __name__=="__main__":
    main()
