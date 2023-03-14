import os
import numpy as np

def saveout_data(
        subj_list_fpath="/scratch/tyoeasley/WAPIAW3/subject_lists/all_subj_eid.csv", 
        patient_list_fpath="/scratch/tyoeasley/WAPIAW3/subject_lists/all_patients_eid.csv", 
        base_outdir="/scratch/tyoeasley/WAPIAW3/fake_data",
        feature_types=["Amplitudes", "NetMats"],
        dim=5
        ):

    with open(subj_list_fpath,'r') as fin:
        subj_list = fin.read().split()

    with open(patient_list_fpath,'r') as fin:
        patient_list = fin.read().split()

    for feature_type in feature_types:
        outpath_type=os.path.join(base_outdir, feature_type, "sub-%s.csv")

        for sID in subj_list:
            if sID in patient_list:
                patient=True
            else:
                patient=False
            outpath = outpath_type % sID

            feature = generate_feature(feature_type, patient, dim=5)
            write_out(outpath, feature)

def generate_feature(feature_type, patient_flag, dim=5):
    if feature_type=="Amplitudes":
        feature = generate_amps(patient_flag, dim=dim)
    elif feature_type=="NetMats":
        feature = generate_NMs(patient_flag, dim=dim)
    else:
        print("Invalid feature type:", feature_type)
        exit()

    return feature


def generate_amps(patient_flag, dim=5):
    feature = np.random.normal(loc=0, size=dim)
    if patient_flag:
        feature = feature + dim
    return feature

def generate_NMs(patient_flag, dim=5):
    if patient_flag:
        x = dim*np.random.rand(dim) + dim - np.random.normal(loc=0, size=(dim,dim))
    else:
        x = np.random.rand(dim,dim)

    feature = np.corrcoef(x)
    return feature


def write_out(outpath, data):
    savedir = os.path.dirname(os.path.abspath(outpath))
    if not os.path.isdir(savedir):
        os.makedirs(savedir)

    np.savetxt(outpath, data)


if __name__=="__main__":
    saveout_data()
