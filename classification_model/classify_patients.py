import argparse
import os
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import ShuffleSplit, GridSearchCV
from sklearn.metrics import accuracy_score, zero_one_loss


##################################################################################################################################
# given a filepath to a list of subject IDs and a general datapath string, returns train-test split data and labels
def get_input_data(subj_list_fpath, data_fpath_type, test_size=0.5, seed_num=0):

    feat_type = os.path.basename(os.path.dirname(data_fpath_type))

    with open(subj_list_fpath,'r') as fin:
        subj_list = fin.read().split()

    # pull imaging data
    X_all = [_pull_data(eid, fpath_type) for eid in subj_list]

    # pull disease group labels
    Y_all = _pull_group_labels(subj_list_fpath)

    X_train, X_test, Y_train, Y_test = train_test_split(
            X_all, 
            Y_all, 
            test_size=0.5, 
            random_state=seed_num+1
            )
    return X_train, X_test, Y_train, Y_test

# loads data for a single subject given a subject ID number and general datapath string
def _pull_data(subj_eid, fpath_type):
    data = np.genfromtxt(fpath_type % subj_eid)
    if len(data.shape) > 1:
        assert len(data.shape) < 3, "classifier expects subject-wise input data to be either a matrix or vector."
        if np.allclose(data, data.T):
            data = _triu_vals(data)
        else:
            data = data.flatten()

    return data

# returns (flattened) upper right triangle of a square matrix; discards matrix diagonal
def _triu_vals(A):
    n = A.shape[0]
    vals = A[np.triu_indices(n,1)]
    return vals


def _pull_group_labels(group_name, label_genpath='/scratch/tyoeasley/WAPIAW3/subj_lists/patient_eid'):
    with open(subj_list_fpath,'r') as fin:
        subj_list = fin.read().split()

    subj_group_name = os.path.basename(subj_list_fpath).split('.')[0]
    
    patient_group_fpath = os.path.join(label_genpath, subj_group_name)
    with open(pateint_group_fpath) as fin:
        patient_set = set(fin.read().split())

    Y_all = [int(eid in patient_set) for eid in subj_list]
    return Y_all
##################################################################################################################################



##################################################################################################################################
# parametrizes learner to user-given (or default) specifications of algorithm and computational resources
def specify_model(n_estimators=250, loss='gini', n_jobs=int(os.environ['OMP_NUM_THREADS']), n_splits=100, folds=5, seed_num=0):
    estimator = RandomForestClassifier(
            n_estimators=n_estimators, 
            criterion=loss,
            n_jobs=1, 
            verbose=1, 
            random_state=seed_num+0
            )
    CV = ShuffleSplit(
            n_splits=n_splits, 
            test_size=0.1,      # reflects 10-fold crossval within training and validation (*not* generalization) dataset
            random_state=seed_num+0
            )
    param_grid = {
            'max_depth': [5, 10, 20, 40, None],
            'max_features': [1, 5, 'log2', 'sqrt', 'auto', None]
            }
    grid_search = GridSearchCV(estimator, param_grid=param_grid,
            cv=folds, 
            verbose=2, 
            n_jobs=n_jobs       # maybe parallelize along learning of splits instead??? -- i.e., use an mp pool to re-learn over CV splits?
            )
    return grid_search, CV
##################################################################################################################################




##################################################################################################################################
# given trained model and held-out validation data, computes mectrics of prediction performance
def predict_collect(y_pred=[], y_true=[], data_collect=[], test_index=[], split=[],
        save_type='validation', modality='ICA150', feature_type='pNMs', group_name='example'):
    import pandas as pd
    scores = {}
    predictions = pd.DataFrame(y_pred, columns=['predicted'])
    predictions['true'] = y_true
    predictions['test_indices'] = pd.DataFrame(test_index,
                                               columns=['test indices'],
                                               index=y_true.index)
    predictions['fold'] = pd.Series([split] * len(predictions),
                                    index=predictions.index)
    data_collect.append(predictions)
    scores['accuracy'] = accuracy_score(y_true, y_pred)     # problem is balanced, so this is equivalent to Jaccard score
    scores['z1_idx'] = zero_one_index(y_true, y_pred)     # normalize=True, so this is equivalent to (normalized) Hamming distance
    scores['fold'] = split
    scores['Estimator'] = 'RandomForest'
    scores['model_testing'] = save_type
    scores['modality'] = modality
    scores['feature_type'] = feature_type
    scores['group'] = group_name 
    return data_collect, scores
##################################################################################################################################




##################################################################################################################################
def_savedir="/scratch/tyoeasley/WAPIAW3/prediction_outputs/"
# learns a patient vs. control classifier (in given group's data) over all shuffle-split data and collects (distributions of)
# prediction outcomes -- maybe implement mp version of this that parallelizes over splits in cv?
def run_and_validate_all_learners(grid_search, CV, X_train, X_test, Y_train, Y_test,
        metrics_outdir=def_savedir):
    metrics = []
    data_collect = []
    gendata_collect = []
    for split, (train_index, val_index) in enumerate(CV.split(X_train, Y_train)):
        scores = {}
        grid_search.fit(X_train[train_index], Y_train[train_index])

        predict_collect(
                y_pred=grid_search.predict(X_train[val_index]), 
                y_true=Y_train[val_index], 
                data_collect=data_collect,
                test_index=val_index,
                split=split, 
                save_type='validation'
                )
        metrics.append(scores)

        predict_collect_save(
                y_pred=grid_search.predict(X_test), 
                y_true=Y_test,
                data_collect=gendata_collect,             
                test_index=np.arange(X_test.shape[0], dtype=np.int),
                split=split, 
                save_type='generalization'
                )
        metrics.append(scores)
    
    # save outputs
    scores = pd.DataFrame(metrics)
    scores.to_csv(os.path.join(savedir, savename))
##################################################################################################################################



##################################################################################################################################
# calls and runs functions given above in proper order
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Binary classification: patient vs. control from resting-state data features")
    parser.add_argument(
            '-l',
            '--subj_list',
            type=str,
            default='/scratch/tyoeasley/WAPIAW3/subject_lists/match_eid/example.csv',
            help='CSV file containing the eids of the subjects to include'
            )
    parser.add_argument(
            '-o',
            '--output_fpath',
            type=str,
            default='/scratch/tyoeasley/WAPIAW3/prediction_outputs/example.csv',
            help='CSV file containing the output of prediction results'
            )
    parser.add_argument(
            '-f',
            '--data_fpath_type',
            type=str,
            ######default='/scratch/tyoeasley/WAPIAW3/subject_lists/match_eid/example.csv',
            ######help='CSV file containing the eids of the subjects to include'
            )
    parser.add_argument(
            '-s',
            '--n_splits',
            type=int,
            default=100,
            help="number of shuffle-splits over which to train new models (per gridsearch)"
            )
    parser.add_argument(
            '-n',
            '--n_jobs',
            type=int,
            default=int(os.environ['OMP_NUM_THREADS']),
            help="number of workers gridsearch learning is allowed to recruit"
            )
    parser.add_argument(
            '-k',
            '--folds',
            type=int,
            default=5,
            help="number of cross-validation folds (within gridsearch)"
            )
    parser.add_argument(
            '-R',
            '--rng_seed',
            type=int,
            default=0,
            help="integer specifying rng state initialization"
            )
    parser.add_argument(
            '-L',
            '--loss',
            type=str,
            default='gini',
            help='loss function of fit model'
            )
    parser.add_argument(
            '-e',
            '--n_estimators',
            type=int,
            default=250,
            help="number of trees (learners) fit per random forest (bag)"
            )
    args = parser.parse_args()
    groupname = ''# get groupname from args.subj_list
    modality, feature_type = ''# get LHS information from fpath_type

    # Add some output
    print('')
    print('Imaging data file:', args.data)
    print('Extra features:', args.extra)
    print('Number of features used:', X_train.shape[1])
    print('List of subjects included in analysis:', args.sub_list)
    print('Number of subjects after selection:', X_train.shape[0] + X_test.shape[0])
    print('Phenotype file:', args.pheno)
    print('Prediction target:', targetType)
    print('Training set size:', X_train.shape[0])
    print('Testing set size:', X_test.shape[0])
    print('Conducting', n_split, 'fold cross-validation.')
    print('Results saved in', os.path.join(savedir, savename))
    print('')



