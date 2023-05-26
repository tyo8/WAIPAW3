import os
import sys
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import ShuffleSplit, GridSearchCV


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

    input_shape = np.floor([input_shape[0]*(1-validation_prop), input_shape[1]])
    param_grid = get_param_grid(input_shape)

    # Parameters of pipelines can be set using '__' separated parameter names:
    grid_search = GridSearchCV(
            pipe, 
            param_grid = param_grid,
            cv = folds, 
            verbose= 1,
            n_jobs = n_jobs
            )
    return grid_search 


def specify_estimator(est_type, params):
    _specify = {
        "RFC": specify_RFC(
            n_estimators = params[0],
            criterion = params[1],
            seed_num = params[2]
            )
        "SVC": specify_SVC(
            n_estimators = params[0],
            criterion = params[1],
            seed_num = params[2]
            )
        "NNC": specify_NNC(
            n_estimators = params[0],
            criterion = params[1],
            seed_num = params[2]
            )
     }
    estimator = _specify.get(est_type, lambda argument: print("Unknown file extension: "+argument))
    return estimator



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
        n_estimators = 250,
        criterion = "gini",
        seed_num=0
        ):
    # ??????????
    estimator = None
#    estimator = RandomForestClassifier(
#            n_estimators = n_estimators,
#            criterion=criterion,
#            verbose=1,
#            random_state=seed_num
#            )
    return estimator

def specify_NNC(
        n_estimators = 250,
        criterion = "gini",
        seed_num=0
        ):
    # ??????????
    estimator = None
#    estimator = RandomForestClassifier(
#            n_estimators = n_estimators,
#            criterion=criterion,
#            verbose=1,
#            random_state=seed_num
#            )
    return estimator




def get_param_grid(input_shape=[254, 400]):
    # Parameters of pipelines can be set using '__' separated parameter names:

    rank = min(input_shape)
#    decomp_dims = [5, 23, 50, 230]
    decomp_dims =[
            int(min(rank,max(1,i))) for i in 
            np.round(np.exp(np.linspace(np.log(rank/100),np.log(rank),5)))
            ]
    param_grid = {
            'dimreduce__n_components': decomp_dims,
            'estimator__max_depth': [5, 10, 20, 40, None],
            'estimator__max_features': [1, 5, 'log2', 'sqrt', None]
            }
    print("Parameter search grid:", param_grid)
    return param_grid
