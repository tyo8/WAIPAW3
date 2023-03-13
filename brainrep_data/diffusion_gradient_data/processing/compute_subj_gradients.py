"""
Created on Thurs Mar 9 2023, 21:07:00 
"""
## Future edit list:
##      a) modularize existing code into
#            0) iterator/tracker (? maybe just write to submit as batch job instead?)
#            1) path-writer for input file, censor file, and output file
#            2) load, censor, and clean data (i.e., remove medial wall)
#            3) compute correlation mtx (flag for undersampling)
#            4) average correlation matrices across (4) subject runs (in tangent space? /flag)
#            5) threshold and re-symmetrize avg corr mtx
#            6) compute diffusion embedding and result (? don't know what that is)
#            7) save per-subject output
#       b) update corr mtx averaging to implement tangent-space projection
#       c) verbose output flag?

import os
import sys
import csv
import h5py
import logging
import datetime
import numpy as np
import nibabel as nib
from sklearn.metrics import pairwise_distances


def seq_HCP_diffusion_maps(subjID_list_fpath, options):
    with open(subjID_list_fpath, newline='') as fin:
        tmp_list = list(csv.reader(fin))
        subjID_list = list(map(''.join, tmp_list))

    for subjID in subjID_list:
        par_HCP_diffusion_maps(subjID, options)


def par_HCP_diffusion_maps(subjID, options):
    
    mask = np.array(nib.load(options.mask_path).get_fdata(), dtype=bool)

    data_list, outpath = pull_subj_data(
            subjID,
            mask=mask,
            outpath_type=options.outpath_type
            )
    dconn = comp_dconn(data_list)
    aff = dconn_to_affinity(dconn,
                            prctile_thresh=options.pthresh)

    ### debug code ###
    # exit()
    ### debug code ###

    emb, res = comp_diffusion_embedding(aff,
                                        alpha=options.alpha,
                                        n_components=options.n_components)

    outpath_emb = export_gradients(outpath, emb, res)
    print('DONE: ' + str(datetime.datetime.now()))


def pull_subj_data(subjID,
                   mask=[],
                   datapath_type="/ceph/biobank/derivatives/melodic/sub-%s/ses-01/sub-%s_ses-01_melodic.ica/filtered_func_data_clean_MNI152.nii.gz",
                   outpath_type="/scratch/tyoeasley/WAPIAW3/brainrep_data/diffusion_gradient_data/subj_gradients/sub-%s.csv"):
    print('\nStep 1: Load data and remove subcortical/cerebellar structrues')
    print(str(datetime.datetime.now()))
    outpath = outpath_type % subjID

    # read in data
    datapath = datapath_type % (subjID, subjID)
    raw_data = nib.load(datapath).get_fdata()

    ### debug code ###
    # np.save("/scratch/tyoeasley/WAPIAW3/brainrep_data/diffusion_gradient_data/processing/unused/raw_data.npy",raw_data)
    ### debug code ###

    # remove unreliable data
    data = np.asarray([raw_data[:,:,:,i][mask] for i in range(raw_data.shape[-1])])

    ### debug code ###
    # np.savetxt("/scratch/tyoeasley/WAPIAW3/brainrep_data/diffusion_gradient_data/processing/unused/masked_data.csv",data)
    ### debug code ###

    data_list = [data]

    return data_list, outpath 



# Step 2: compute correlation matrix
def comp_dconn(data_list, subsample_flag=True, subsample_factor=0.10):
    print('\nStep 2: compute correlation matrix')
    startime = datetime.datetime.now()

    corr_data_list = [_comp_corr_mtx(data,
                                     subsample=subsample_flag,
                                     subsample_factor=subsample_factor) for data in data_list]
    nan_num = np.sum(np.array(~np.isnan(corr_data_list)) + 0, axis=0)
    dconn = np.nansum(corr_data_list, axis=0) / nan_num

    lapsetime = datetime.datetime.now() - startime
    print('Compute time for correlation matrix: ' + str(lapsetime))

    return dconn


def _comp_corr_mtx(data, subsample=True, subsample_factor=0.10):

    if subsample:

        # compute subsampled correlation matrix
        data = data - np.mean(data, axis=0)
        data_variance = np.linalg.norm(data, axis=0)
        non_null_idx = [ idx for idx,var in enumerate(data_variance) if var > 0 ]

        print("proportion of non-null columns (after centering):", len(non_null_idx)/len(data_variance))
        data = data[:, non_null_idx]
        data_variance = data_variance[non_null_idx]

        varnorm_data = data / data_variance
        
        ### debug code ###
        numNaNs_vdata = np.count_nonzero(np.isnan(varnorm_data))
        assert numNaNs_vdata == 0, "found NaN values in variance-normalized data!"
        ### debug code ###

        # find subsample indices for given factor
        # set random number generator
        np.random.seed(1)
        N = data.shape[1]
        subsample_idx = np.random.randint(0, N, int(N * subsample_factor))

        ### debug code ###
        print(f"Maximum subsample idx (length {len(subsample_idx)}):", max(subsample_idx))
        ### debug code ###

        corr_data = np.matmul(np.transpose(varnorm_data), varnorm_data[:, subsample_idx])
        
        ### debug code ###
        numNaNs_corrdata = np.count_nonzero(np.isnan(corr_data))
        print("number of NaN values in corrdata:", numNaNs_corrdata) 
        ### debug code ###
    else:
        # compute correlation matrix
        corr_data = np.corrcoef(data)

    return np.single(corr_data)


def dconn_to_affinity(dconn, prctile_thresh=90):
    print('Dconn shape: ' + str(dconn.shape))
    print('subsampling factor = ' + str(float(dconn.shape[1]) / float(dconn.shape[0])))

    startime = datetime.datetime.now()
    perc = np.array([np.percentile(x, prctile_thresh) for x in dconn])

    for i in range(dconn.shape[0]):
        dconn[i, dconn[i, :] < perc[i]] = 0

    lapsetime = datetime.datetime.now() - startime
    print('Thresholding (elapsed time): ' + str(lapsetime))
    print("Minimum value is %f" % dconn.min())

    a = dconn < 0
    b = np.sum(a, 1)
    c = b != 0
    d = np.sum(c)
    print('\nStep 3: remove negative')

    print("Negative values occur in %d rows" % d)

    dconn[dconn < 0] = 0

    print('\nStep 4: generate affinity matrix')
    print(str(datetime.datetime.now()))

    startime = datetime.datetime.now()
    aff = 1 - pairwise_distances(dconn, metric='cosine')
    print("affinity matrix has size:", aff.shape)

    lapsetime = datetime.datetime.now() - startime
    temp_str = 'Compute time of affinity matrix: ' + str(lapsetime)
    print(temp_str)
    return aff


def comp_diffusion_embedding(aff, alpha=0.5, n_components=10):
    from mapalign import embed
    # Generate embeddings
    print('\nStep 5: perform diffusion embedding')
    print('n_components = ' + str(n_components))

    startime = datetime.datetime.now()
    embedding, results = embed.compute_diffusion_map(aff, alpha=alpha, n_components=n_components, return_result=True)
    print("embedding has shape:", embedding.shape)
    print("results:", results)

    lapsetime = datetime.datetime.now() - startime
    print('embedding done in: ' + str(lapsetime))
    return embedding, results


# NOTE: input variable 'outpath_type' should contain a '%s' substring to receive 'emb' & 'res' (i.e., results type) designations
def export_gradients(outpath_type, embedding, results=None):
    print('\nSaving results...')

    fpath_emb = outpath_type.replace('.csv','_emb.csv')
    if results:
        fpath_res = outpath_type.replace('.csv','_res.npy')

    savedir = os.path.dirname(os.path.abspath(fpath_emb))

    # check existence of output directory; make if nonexistent
    if not os.path.isdir(savedir):
        os.makedirs(savedir)
        print('WARNING: created directory ' + savedir)

    np.savetxt(fpath_emb, embedding)
    if results:
        np.save(fpath_res, results)

    return fpath_emb


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Compute diffusion embedding of data for every subject in list')
    parser.add_argument('subjects',
                        help='Path to list of subject IDs expected if sequential OR subject ID number expected if parallel')
    parser.add_argument('--par',
                        dest='par_flag', default=False, action='store_const', const=True,
                        help='Logical flag: to distribute or not to distribute?')
    parser.add_argument('-o', '--out',
                        dest='outpath_type', type=str,
                        default="/scratch/tyoeasley/WAPIAW3/brainrep_data/diffusion_gradient_data/subj_gradients/sub-%s.csv",
                        help='string containing generic output destination')
    parser.add_argument('-m', '--mask_path', type=str,
                        default="/scratch/tyoeasley/WAPIAW3/brainrep_data/final_GM_mask.nii.gz",
                        help='filepath to data mask (in MNI standard space)')
    parser.add_argument('--pthresh',
                        dest='pthresh', default=90, type=int,
                        help='Percentile threshold for connectivity matrix thresholding (used only if tanproj_flag=False)')
    parser.add_argument('-n', '--n_components',
                        dest='n_components', default=40, type=int,
                        help='Number of components (i.e., coordinates) to keep from diffusion embedding')
    parser.add_argument('-a', '--alpha',
                        dest='alpha', default=0.5, type=float,
                        help='Diffusion embedding parameter')
    args = parser.parse_args()

    if args.par_flag:
        subjID = args.subjects
        par_HCP_diffusion_maps(subjID, args)
    else:
        subjID_fpath = args.subjects
        seq_HCP_diffusion_maps(subjID_fpath, args)
