import os
import csv
import sys
import numpy as np
import nibabel as nb

profumo_outdir = '/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/out_PROFUMO/rmed_G8_eid_wapiaw_25_Results.ppp'

def write_out(outpath, data):
    savedir = os.path.dirname(os.path.abspath(outpath))
    if not os.path.isdir(savedir):
        os.makedirs(savedir)

    np.savetxt(outpath, data)


if __name__ == "__main__":
    profumo_outdir = sys.argv[1]
    genpath=os.path.join(profumo_outdir, 'Maps/')
    subjID_path='/scratch/tyoeasley/WAPIAW3/subject_lists/all_subj_eid.csv'
    mask=nb.load('/scratch/tyoeasley/WAPIAW3/brainrep_data/final_GM_mask.nii.gz')
    mask_data = mask.get_fdata()
    with open(subjID_path, newline='') as fin:
        subjID_list = list(map(''.join, list(csv.reader(fin))))

    # genpath_in = genpath + 'sub-%s.dscalar.nii'
    genpath_in = genpath + 'sub-%s.nii.gz'
    outputpath = os.path.join(profumo_outdir, 'spatialNMs/')
    genpath_out = outputpath + 'sub-%s.csv'

    for sID in subjID_list:
        try:
            fpath = genpath_in % sID
            ts_data = nb.load(fpath).get_fdata()
            masked_data = ts_data.copy()
            masked_data = masked_data[mask_data == 1]
            if masked_data.shape[0] > masked_data.shape[1]:
                masked_data = masked_data.T
        # ts_data = ts_data[good_modes,:]
        except IOError:
            err_log = open('missing_subj_data.csv', 'a')
            err_log.write(fpath + '\n')
            err_log.close()
            continue
        spNM = np.corrcoef(masked_data)

        outpath = genpath_out % sID
        write_out(outpath, spNM)
