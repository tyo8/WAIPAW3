import os
import re
import sys
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict


# given a filepath to a list of subject IDs and a general datapath string, returns train-test split data and labels
def get_input_data(subj_list_fpath,subj_group_flist, datapath_type, test_prop=0.1, seed_num=0, patient_eid_dir='', verbose=True):

    with open(subj_list_fpath,'r') as fin:
        subj_list = fin.read().split()
    
    with open(subj_group_flist,'r') as fin:
        group_path_list = fin.read().split()

    grouplist = [re.search(r"rmed_.+?_eid_wapiaw", path).group() for path in group_path_list if re.search(r"rmed_.+?_eid_wapiaw", path)]

    # pull imaging data
    X_all = np.array([_pull_subj_data(eid, datapath_type) for eid in subj_list], dtype=float)


    ### debug code ###
    print("Full data array has shape:", X_all.shape)
    # print("Data array:", X_all)
    ### debug code ###

    # pull disease group labels
    Y_all = np.asarray(_pull_group_labels(subj_list_fpath, patient_eid_dirs))
    #print("Y:",Y_all.shape)


    return X_all, Y_all

# loads data for a single subject given a subject ID number and general datapath string
def _pull_subj_data(subj_eid, datapath_type):
    for label in label_set:
        if label != 'health':
            groupname = "rmed_" + label.replace('_unique', '') + "_eid_wapiaw"
            path = os.path.join(combined_eid_dirs, label)
            with open(path) as fin:
                patient_set = set(fin.read().split())
            if subj_eid in patient_set:
                break

    # datapath = datapath_type % (groupname, subj_eid)
    datapath = datapath_type % subj_eid
    data = np.genfromtxt(datapath)
    if np.isnan(data).any():
        if datapath.endswith(".csv"):
            data = np.genfromtxt(datapath, delimiter=",")
            if np.isnan(data).any():
                raise Exception("At least one nan value in loaded data -- probably not a load-in error.")
        elif datapath.endswith(".txt"):
            raise Exception("At least one nan value in loaded data -- probably not a load-in error.")
        else:
            raise Exception(f"At least one nan value in loaded data -- did you mean to have a \".{datapath.split('.')[-1]}\" file extension?")


    if len(data.shape) > 1:
        assert len(data.shape) == 2, "classifier expects subject-wise input data to be either a matrix or vector."
        if data.shape == data.T.shape:
            if np.allclose(data, data.T,rtol=1e-4, atol=1e-6):  # changed tolerence
                data = _triu_vals(data)
                data = _handle_corrs(data)
            else:
                data = data.flatten()
        else:
            data = data.flatten()

    ### debug code ###
    # print(f"subect {subj_eid} has data of shape:", data.shape)
    ### debug code ###

    return np.array(data.flatten(), dtype=float)

# returns (flattened) upper right triangle of a square matrix; discards matrix diagonal
def _triu_vals(A):
    n = A.shape[0]
    vals = A[np.triu_indices(n,1)]
    return vals.flatten()

def _handle_corrs(data):
    if (np.abs(data.flatten()) <= 1).all():
        new_data = np.arctanh(data)
    else:
        new_data = data
    return new_data

def _pull_group_labels(subj_list_fpath, patient_eid_dirs):
    
    with open(subj_list_fpath,'r') as fin:
        subj_list = fin.read().split()
     
    full_paths = [os.path.join(patient_eid_dirs, label) for label in label_set]
    
    label_to_int = {label: i for label, i in zip(labels, indices)} # actual group name to index like 0-17
    
    Y_all = [0] * len(subj_list) 
    for path in full_paths:
        with open(path) as fin:
            patient_set = set(fin.read().split())

        # label_to_int.get():check if the the path point to the group we want, -100 for NO, int for YES.
        # int(eid in patient_set): check if the eid in this group,0 for NO,1 for YES.
        Y = [label_to_int.get(os.path.basename(path), -100)*int(eid in patient_set) for eid in subj_list]
        # Y presents the int where the eid is in this group, 0 if the eid is not.
        # Y_all adds all the Y from loop, so every eid matchs to their label.
        Y_all = [a + b for a, b in zip(Y, Y_all)]


    return Y_all

def fit_multiclass(n_estimators = 10,criterion = "gini",random_state = 42):
    clf = OneVsRestClassifier(
            RandomForestClassifier(
                n_estimators = n_estimators,
                criterion = criterion,
                random_state = random_state)
            )

    return clf


if __name__=="__main__":
    brainrep=sys.argv[1]
    feature=sys.argv[2]
    dim=sys.argv[3]
    datapath_type=sys.argv[4]

    base_dir="/scratch/tyoeasley/WAPIAW3"
    subj_group_flist="/scratch/tyoeasley/WAPIAW3/subject_lists/lists_of_groups/code_disease_groups_noStruct.txt" 
    subj_list_fpath='/scratch/tyoeasley/WAPIAW3/subject_lists/all_subj_eid_uni_noStruct.csv'
    patient_eid_dirs='/scratch/tyoeasley/WAPIAW3/subject_lists/patient_eid_unique_noStruct'
    combined_eid_dirs='/scratch/tyoeasley/WAPIAW3/subject_lists/combined_subj_eid_unique'
       
    
    label_set = ['F0_unique', 'F10_unique', 'F17_unique', 'F32_unique', 'F41_unique',
                 'G2_unique', 'G35_37_unique', 'G40_unique', 'G43_unique', 'G45_unique', 
                 'G47_unique', 'G55_unique', 'G56_unique', 'G57_unique', 'G62_unique', 'G8_unique', 'G93_unique', 'health' ]
    indices, labels = pd.factorize(label_set)

    #################################################################################################################################################
    X_all, Y_all = get_input_data(
            subj_list_fpath,
            subj_group_flist, 
            datapath_type,
            test_prop=0.1, 
            seed_num=0, 
            patient_eid_dir=patient_eid_dirs, 
            verbose=True
            )
    
    #################################################################################################################################################
    ### TRY TO PUT ALL FITTING CODE INTO SINGLE FUNCTION, BUT SEPARATE FROM METRIC (?) COMPUTATION ###
    clf = fit_multiclass(n_estimators = 250,criterion = "gini",random_state = 42)
    #################################################################################################################################################

    #################################################################################################################################################
    ### WHAT IS THE MINIMUM SET OF (sufficiently flexible) INPUTS TO MAKE THIS CODE SECTION INTO A FUNCTION? WHAT OUTPUTS SHOULD IT HAVE? ###
    y_pred = cross_val_predict(clf, X_all, Y_all, cv=10) # cv (Stratified)KFold
    result = np.column_stack((Y_all, y_pred))
    df = pd.DataFrame(result)
    df.to_csv(f"/scratch/tyoeasley/WAPIAW3/multiclass/output/{brainrep}_{feature}.csv",index=False, header=False)
