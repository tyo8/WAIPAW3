import sys
import nibabel as nib

if __name__=="__main__":
    filename=sys.argv[1]
    nib.load(filename)
