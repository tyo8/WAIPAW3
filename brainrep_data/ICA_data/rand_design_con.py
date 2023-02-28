import sys
import argparse
import numpy as np


def random_design(N, fpath_out='', C=2):
    des_vec = np.round(np.random.rand(N,1))
    des_mtx = np.concatenate((des_vec, 1-des_vec), 1)
    des_mtx = des_mtx.astype(int)
    if fpath_out:
        np.savetxt(fpath_out,des_mtx,fmt='%.1d')
    else:
        return des_mtx

def arb_contrast(fpath_out='', C=2):
    contrast_mtx = np.eye(C)
    if fpath_out:
        np.savetxt(fpath_out,contrast_mtx,fmt='%.1d')
    else:
        return contrast_mtx


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate subindex samplings and their unique tags"
    )
    parser.add_argument(
        "-f", "--fpath_noext", type=str, default='design', help="filepath to design/contrast matrices (no extension)"
    )
    parser.add_argument(
        "-n", "--n_subj", type=int, default=140, help="number of subjects"
    )
    parser.add_argument(
        "-c", "--contrasts", type=int, default=2, help="number of contrasts"
    )

    args = parser.parse_args()

    des_fpath = args.fpath_noext + '.mat'
    con_fpath = args.fpath_noext + '.con'

    random_design(args.n_subj, fpath_out=des_fpath, C=args.contrasts)
    arb_contrast(fpath_out=con_fpath, C=args.contrasts)
