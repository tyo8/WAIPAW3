import os
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import KFold
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, zero_one_loss
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import multilabel_confusion_matrix, ConfusionMatrixDisplay

# given a filepath to a list of subject IDs and a general datapath string, returns train-test split data and labels
def get_input_data(subj_list_fpath, datapath_type, test_prop=0.1, seed_num=0, patient_eid_dir='', verbose=True):

    with open(subj_list_fpath,'r') as fin:
        subj_list = fin.read().split()

    # pull imaging data
    X_all = np.array([_pull_subj_data(eid, datapath_type) for eid in subj_list], dtype=float)

    ### debug code ###
    print("Full data array has shape:", X_all.shape)
    # print("Data array:", X_all)
    ### debug code ###

    # pull disease group labels
    Y_all = np.asarray(_pull_group_labels(subj_list_fpath, patient_eid_dirs)[0])
    #print("Y:",Y_all.shape)

    if verbose:
        _output_params(X_all, Y_all)

    return X_all, Y_all

# loads data for a single subject given a subject ID number and general datapath string
def _pull_subj_data(subj_eid, datapath_type):
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
    label_set = os.listdir(patient_eid_dirs)
    factor = pd.factorize(label_set)
    labels, indices = factor[0], factor[1]
    
    with open(subj_list_fpath,'r') as fin:
        subj_list = fin.read().split()
    
    full_paths = [os.path.join(patient_eid_dirs, label) for label in label_set]
    
    label_to_int = {label: i for i, label in zip(labels, indices)}
   # print(label_to_int) 
    Y_all = [0] * len(subj_list)
    for path in full_paths:
        with open(path) as fin:
            patient_set = set(fin.read().split())
        Y = [label_to_int.get(os.path.basename(path), -100)*int(eid in patient_set) for eid in subj_list]
        Y_all = [a + b for a, b in zip(Y, Y_all)]

    return Y_all,factor

def _output_params(X_train, X_test):
    print('')
    print('Testing set size:', X_test.shape)
    print('Training set size:', X_train.shape)
    print('Number of features used:', X_train.shape[1])
    print('Number of subjects after selection:', X_train.shape[0] + X_test.shape[0])
    print('')

subj_list_fpath='/scratch/tyoeasley/WAPIAW3/subject_lists/all_subj_eid_uni.csv'
#subj_list_fpath='/scratch/tyoeasley/WAPIAW3/subject_lists/test.csv'
patient_eid_dirs='/scratch/tyoeasley/WAPIAW3/subject_lists/patient_eid_unique'
datapath_type = '/scratch/tyoeasley/WAPIAW3/brainrep_data/T1_data/Volumes/sub-%s.csv'
datapath_type = '/scratch/tyoeasley/WAPIAW3/brainrep_data/T1_data/Surface/sub-%s.csv'
datapath_type = '/scratch/tyoeasley/WAPIAW3/brainrep_data/Schaefer_data/NetMats/sub-%s.csv'
X_all, Y_all = get_input_data(subj_list_fpath, datapath_type, test_prop=0.1, seed_num=0, patient_eid_dir=patient_eid_dirs, verbose=True)
Y_all,label_factor = _pull_group_labels(subj_list_fpath, patient_eid_dirs)

clf = OneVsRestClassifier(RandomForestClassifier(n_estimators = 10,criterion = "gini",random_state = 42))
#Y_predict = clf.predict(X_test)
#print(Y_predict)
#print(Y_test)

cv = ShuffleSplit(n_splits=10, test_size=0.1, random_state=42)
scores = cross_val_score(clf, X_all, Y_all, cv=cv,scoring='roc_auc')
#print(scores)
avg_score = np.mean(scores)
print("Average Accuracy:", avg_score)

y_pred = cross_val_predict(clf, X_all, Y_all, cv=10)
fold_size = len(Y_all) // 10
cm=[]
for fold in range(10):
    start_idx = fold * fold_size
    end_idx = start_idx + fold_size
    fold_y_test = Y_all[start_idx:end_idx]
    fold_y_pred = y_pred[start_idx:end_idx]
    cm.append(confusion_matrix(fold_y_test, fold_y_pred))

print(cm)

cm = np.sum(cm,axis=0).astype(np.int16)



labels = label_factor[1]
class_names = label_factor[0]
print(class_names)

# Plot confusion matrix in a beautiful manner
fig = plt.figure(figsize=(16, 14))
ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax, fmt = 'g'); #annot=True to annotate cells
# labels, title and ticks
ax.set_xlabel('Predicted', fontsize=20)
ax.xaxis.set_label_position('bottom')
plt.xticks(rotation=90)
ax.xaxis.set_ticklabels(labels, fontsize = 10)
ax.xaxis.tick_bottom()

ax.set_ylabel('True', fontsize=20)
ax.yaxis.set_ticklabels(labels, fontsize = 10)
plt.yticks(rotation=0)

plt.title('Schaefer_NM  Confusion Matrix', fontsize=20)

plt.savefig('/home/l.lexi/Schaefer_NM_confusion.png')
