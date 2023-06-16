import os
import argparse
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score
from model_specification import specify_model as specify_model
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit

##################################################################################################################################
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
    Y_all = np.asarray(_pull_group_labels(subj_list_fpath, patient_eid_dir=patient_eid_dir))

    if test_prop > 0:
        X_train, X_test, Y_train, Y_test = train_test_split(
                X_all, 
                Y_all, 
                test_prop=test_prop, 
                random_state=seed_num+1
                )
    else:
        X_train = X_all
        Y_train = Y_all
        X_test = np.asarray([])
        Y_test = np.asarray([])

    if verbose:
        _output_params(X_train, X_test)

    return X_train, X_test, Y_train, Y_test

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
    print(f"subect {subj_eid} has data of shape:", data.shape)
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

def _pull_group_labels(subj_list_fpath, patient_eid_dir=''):
    with open(subj_list_fpath,'r') as fin:
        subj_list = fin.read().split()

    subj_group_fname = os.path.basename(subj_list_fpath)
    
    patient_group_fpath = os.path.join(patient_eid_dir, subj_group_fname)
    with open(patient_group_fpath) as fin:
        patient_set = set(fin.read().split())

    Y_all = [int(eid in patient_set) for eid in subj_list]
    return Y_all

# sends information about learning problem parameters to output stream
def _output_params(X_train, X_test):
    print('')
    print('Testing set size:', X_test.shape)
    print('Training set size:', X_train.shape)
    print('Number of features used:', X_train.shape[1])
    print('Number of subjects after selection:', X_train.shape[0] + X_test.shape[0])
    print('')
##################################################################################################################################



##################################################################################################################################
# given the result metrics outpath, extracts 'feature' and 'brain_rep' types of input data: expects outpath to have basename of
# the form "metrics_<groupname>_<brain_rep>_<feature>.csv"
def _extract_metadata(outpath):
    outname = os.path.basename(outpath).split('.')[0]
    
    if "partial_NM" in outname:
        feature_type = "partial_NMs"
    else:
        feature_type = outname.split('_')[-1]

    brain_rep = outname.replace('metrics_','').replace(feature_type,'').split('_')[-2]
    
    return brain_rep, feature_type
##################################################################################################################################



##################################################################################################################################
# learns a patient vs. control classifier (in given group's data) over all shuffle-split data and collects (distributions of)
# prediction outcomes -- maybe implement mp version of this that parallelizes over splits in cv?
def fit_and_save_all_models(grid_search, X_train, Y_train, 
        X_test=[], Y_test=[], n_splits=100, validation_prop=0.2, seed_num=0,
        outpath='predictions.csv', brain_rep='ICA_d150', feature_type='pNMs', group_name='example'):
    metrics = []
    data_collect = []
    gendata_collect = []

    CV = StratifiedShuffleSplit(
            n_splits  = n_splits,
            test_size = validation_prop,
            random_state = seed_num
            )

    for split, (train_index, val_index) in enumerate(CV.split(X_train, Y_train)):
        grid_search.fit(X_train[train_index], Y_train[train_index])

        data_collect, scores = _predict_collect(
                y_pred=grid_search.predict(X_train[val_index]), 
                y_true=Y_train[val_index], 
                data_collect=data_collect,
                test_index=val_index,
                split=split, 
                save_type="validation",
                brain_rep=brain_rep,
                feature_type=feature_type,
                group_name=group_name
                )
        metrics.append(scores)

        if np.any(X_test) and np.any(Y_test):
            gendata_collect, scores = _predict_collect(
                    y_pred=grid_search.predict(X_test), 
                    y_true=Y_test,
                    data_collect=gendata_collect,             
                    test_index=np.arange(X_test.shape[0], dtype=int),
                    split=split, 
                    save_type='generalization',
                    brain_rep=brain_rep,
                    feature_type=feature_type,
                    group_name=group_name
                    )
            metrics.append(scores)

        # save outputs (iterative)
        if split==0:
            pd.DataFrame(metrics).to_csv(outpath, mode='w')
        else:
            pd.DataFrame(metrics[-1]).to_csv(outpath, mode='a', header=False)

    
# given trained model and held-out generalization data, computes mectrics of prediction performance
def _predict_collect(y_pred=[], y_true=[], data_collect=[], test_index=[], split=[],
        save_type='validation', brain_rep='ICA_d150', feature_type='pNMs', group_name='example'):
    import pandas as pd
    scores = {}
    predictions = pd.DataFrame(y_pred, columns = ['predicted'])
    predictions['true'] = y_true
    predictions['fold'] = pd.Series([split] * len(predictions),
                                    index=predictions.index)
    data_collect.append(predictions)
    scores['accuracy'] = accuracy_score(y_true, y_pred)     # problem is balanced, so this is equivalent to Jaccard score
    # scores['roc_auc'] = roc_auc_score(y_true, y_pred)
    scores['fold'] = split
    scores['Estimator'] = 'RandomForest'
    scores['model_testing'] = save_type
    scores['brain_rep'] = brain_rep
    scores['feature_type'] = feature_type
    scores['group'] = group_name
    ### debug code ###
    print("scores for split ", split, ": ", scores)
    ### debug code ###
    return data_collect, scores
##################################################################################################################################



##################################################################################################################################
# parses inputs, generates derivative intermediates, loads and splits data, fits and predicts with RF classifiers, and saves results
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Binary classification: patient vs. control from resting-state data features")
    parser.add_argument(
            '-l',
            '--subj_list',
            type=str,
            default='/scratch/tyoeasley/WAPIAW3/subject_lists/combined_subj_eid/example.csv',
            help='CSV file containing the eids of the subjects to include'
            )
    parser.add_argument(
            '-f',
            '--datapath_type',
            type=str,
            default="/scratch/tyoeasley/WAPIAW3/brainrep_data/ICA_data/dual_regression/example/ica25/Amplitudes/sub-%s.csv",
            help="generic path (awaiting eid substitution) to CSV file containing per-subject features"
            )
    parser.add_argument(
            '-o',
            '--outpath',
            type=str,
            default='/scratch/tyoeasley/WAPIAW3/prediction_outputs/example_ica25_Amplitudes.csv',
            help='CSV file containing the output of prediction results'
            )
    parser.add_argument(
            '-s',
            '--n_splits',
            type=int,
            default=100,
            help="number of shuffle-splits over which to train new models (per gridsearch)"
            )
    parser.add_argument(
            '-C',
            '--classifier_type',
            type=str,
            default="RFC",
            help="type of classfification algorithm to use (refers estimator-type object in sklearn)"
            )
    parser.add_argument(
            '-n',
            '--n_jobs',
            type=int,
            default=1,
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
            default="gini",
            help='loss function of fit model'
            )
    parser.add_argument(
            '-e',
            '--n_estimators',
            type=int,
            default=250,
            help="number of trees (learners) fit per random forest (bag)"
            )
    parser.add_argument(
            '-p',
            '--patient_eid_dir',
            type=str,
            default='/scratch/tyoeasley/WAPIAW3/subject_lists/patient_eid',
            help="directory containing lists of patient eid numbers"
            )
    parser.add_argument(
            '-v',
            '--verbose',
            default=False,
            action='store_true',
            help="verbose flag: send problem parameters to output stream?"
            )
    args = parser.parse_args()
    group_name = os.path.basename(args.subj_list).split('.')[0]          # get group_name from args.subj_list
    brain_rep, feature_type = _extract_metadata(args.outpath)    # get LHS information from datapath_type

    test_prop = 0                   # not passed in through parser because this quantity is not allowed to vary for different calls
    # test_prop = 0.1               # not passed in through parser because this quantity is not allowed to vary for different calls
    validation_prop = 0.2           # not passed in through parser because this quantity is not allowed to vary for different calls

    # verbose output
    if args.verbose:
        print('')
        print('Subject group in analysis:', group_name)
        print('Brain representation type:', brain_rep)
        print('Feature type:', feature_type)
        print('Conducting', args.n_splits, f"validate-train shuffle-splits (validation_prop={validation_prop}).")
        print('Saving results to:', args.outpath)

    X_train, X_test, Y_train, Y_test = get_input_data(
            args.subj_list, 
            args.datapath_type, 
            patient_eid_dir = args.patient_eid_dir,
            test_prop = test_prop,                              # not passed in through parser because this quantity is not allowed to vary for different calls
            seed_num = args.rng_seed, 
            verbose = args.verbose
            )

    grid_search = specify_model(
            n_estimators = args.n_estimators, 
            estimator_criterion = args.loss, 
            n_jobs = args.n_jobs,
            folds = args.folds, 
            seed_num = args.rng_seed,
            input_shape = X_train.shape,
            validation_prop = validation_prop,                  # not passed in through parser because this quantity is not allowed to vary for different calls
            estimator_type = args.classifier_type
            )

    fit_and_save_all_models(grid_search, X_train, Y_train, 
            X_test = X_test, 
            Y_test = Y_test,
            n_splits = args.n_splits, 
            validation_prop = validation_prop,                  # not passed in through parser because this quantity is not allowed to vary for different calls
            seed_num = args.rng_seed,
            outpath = args.outpath, 
            brain_rep = brain_rep, 
            feature_type = feature_type, 
            group_name = group_name
            )
