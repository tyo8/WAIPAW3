import os
import sys
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import ShuffleSplit, GridSearchCV

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

# REWRITE THIS TO USE **kwargs PYTHON FORMALISM
def specify_model(
        n_estimators = 250,
        estimator_criterion = '',
        n_splits = 100,
        folds = 5,
        n_jobs = 1,
        seed_num = 0,
        validation_prop = 0.2,
        dimreduce = PCA(), 
        scaler = StandardScaler(), 
        estimator_type = "RFC",
        input_shape = [254, 17900]
        ):

    # Define a Standard Scaler to normalize inputs
    estimator_params = [n_estimators, estimator_criterion, seed_num]
    estimator = specify_estimator(estimator_type, estimator_params)
    
    pipe = Pipeline(steps=[("scaler", scaler), ("dimreduce", dimreduce), ("estimator", estimator)])

    rank = min(np.floor([input_shape[0]*(1-validation_prop), input_shape[1]]))
    print("rank of data given to gridsearch:", rank)
    param_grid = get_param_grid(rank, estimator_type)

    # Parameters of pipelines can be set using '__' separated parameter names:
    grid_search = GridSearchCV(
            pipe, 
            param_grid = param_grid,
            cv = folds, 
            verbose= 1,
            n_jobs = n_jobs,
            scoring = 'roc_auc'
            )
    return grid_search 

def specify_RFC(
        n_estimators = 250,
        criterion = "gini",
        seed_num=0
        ):
    estimator = RandomForestClassifier(
            n_estimators = n_estimators,
            criterion=criterion,
            verbose=1,
            random_state=seed_num
            )
    return estimator

def specify_SVC(
        C = 1,  # regularization parameter: the larger C is, the less regularized the SVC (i.e., the smaller the allowed max margin as stopping criteria)
        kernel = "linear" #used to be rbf
        ):
    estimator = SVC(
            C = C,
            kernel = kernel,
            verbose=1
            )
    return estimator

def specify_KNC(
        n_neighbors = 5,
        metric = 'minkowski'
        ):
    estimator = KNeighborsClassifier(
            n_neighbors = n_neighbors,
            metric = metric,
            #verbose=1
            )
    return estimator

def specify_estimator(est_type, params):
    _specify = {
        'RFC': specify_RFC(
            n_estimators = params[0],
            criterion = params[1],
            seed_num = params[2]
            ),
        'SVC': specify_SVC(
            C = params[0],
            kernel = params[1]
            ),
        'KNC': specify_KNC(
            n_neighbors = params[0],
            metric = params[1]
            )
     }
    estimator = _specify.get(est_type, lambda argument: print("Unknown file extension: "+argument))
    return estimator






def get_param_grid(rank, est_type):
    # Parameters of pipelines can be set using '__' separated parameter names:

    #    decomp_dims = [5, 23, 50, 230]
    log_r = np.log10(rank)
    decomp_dims =[
            int(min(rank,max(1,i))) for i in 
            np.round(np.logspace(log_r-2, log_r, num=5))
            ]
    if est_type == 'RFC':
        param_grid = {
                'dimreduce__n_components': decomp_dims,
                'estimator__max_depth': [5, 10, 20, 40, None],
                'estimator__max_features': [1, 5, 'log2', 'sqrt', None]
                }
        print("Parameter search grid:", param_grid)
    elif est_type == 'SVC':
        param_grid = {
                'dimreduce__n_components': decomp_dims,
                'estimator__C': np.logspace(-3, 3, num=7),
                'estimator__kernel': ['linear','rbf', 'sigmoid', 'poly']
                }
    elif est_type == 'KNC':
        param_grid = {
                'dimreduce__n_components': decomp_dims,
                'estimator__n_neighbors': [int(i) for i in (np.arange(1,10,2)**1.5)],
                'estimator__weights': ['uniform', 'distance'],
                'estimator__metric': ['l1', 'l2', 'cosine']
                }

    return param_grid
