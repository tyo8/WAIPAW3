import os
import sys
import glob
import numpy as np

def clean_PROFUMO_NMs(NM_dir):
    fpath_list = glob.glob(os.path.join(NM_dir,'sub-*.csv'))
    for fpath in fpath_list:
        data = clean_NM(fpath)
        np.savetxt(fpath,data)

def clean_NM(fpath):
    orig_data = np.genfromtxt(fpath, delimiter=" ")
    ndims = len(orig_data.shape)
    if ndims < 2:
        N = np.sqrt(len(orig_data))
        assert N==int(N), "non-square number of entries in vectorized load-in >:[ bad!"
        N = int(N)
        data = np.reshape(orig_data, [N, N])
    else:
        dims = orig_data.shape
        assert dims[0]==dims[1], "non-square number of entries in vectorized load-in >:[ bad!"
        data = orig_data

    try:
        assert np.allclose(data, data.T, rtol=1e-4, atol=1e-6), "network matrix must be symmetric (within machine error)"
    except AssertionError:
        print(f"raw data: {data}")
        print(f"data shape: {data.shape}")
        print(f"saw NaN values: {np.isnan(data).any()}")
        exit()

    return data

if __name__=="__main__":
    NM_dir = sys.argv[1]
    clean_PROFUMO_NMs(NM_dir)
