import os
import sys
import nibabel as nib

if __name__=="__main__":
    filename=sys.argv[1]
    test_arr=nib.load(filename).get_fdata() 
