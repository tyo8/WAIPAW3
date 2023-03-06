import argparse
import os
from os import path
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import ShuffleSplit, GridSearchCV
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                             explained_variance_score, r2_score)


# Parsing parameters
parser = argparse.ArgumentParser(description='Predicting subject traits with imaging data')
#####################################################################################################################################################################
# probably stil keep this
parser.add_argument('-l', '--list',
    default='/scratch/janine.bijsterbosch/WAPIAW_2/subj_lists/sub_list_med.csv',
    help='CSV file containing the eids of the subjects to include', dest='sub_list')
#####################################################################################################################################################################
#####################################################################################################################################################################
# change this to file with list of imaging data filepaths?
parser.add_argument('-d', '--data',
    default='/scratch/janine.bijsterbosch/WAPIAW_2/imaging/task_residuals_separate_proj.npy',
    help='File containing the imaging data (n_sub * n_feature numpy array)', dest='data')
#####################################################################################################################################################################

#####################################################################################################################################################################
# can probably be combined into one argument
parser.add_argument('-p', '--phenotypes',
    default='/scratch/janine.bijsterbosch/WAPIAW_2/phenotypes/WAPIAW2_clean.tsv',
    help='TSV file containing the phenotype data', dest='pheno')
parser.add_argument('-t', '--target', default='20016-2.0', choices=['20016-2.0', '20016_Mean', '20127-0.0', '20127_Mean', '21003-2.0'],
    help='Prediction target, "20016-2.0" or "20016_Mean" for fluid intelligence, "20127-0.0" or "20127_Mean" for neuroticism, and "21003-2.0" for age', dest='target')
#####################################################################################################################################################################

parser.add_argument('-o', '--output',
    default='/scratch/janine.bijsterbosch/WAPIAW_2/task_residuals/prediction/scores.csv',
    help='File to save the results (will add a "+" if the file exists).', dest='output')
parser.add_argument('-s', '--splits', type=int, default=100,
    help='Number of splits for cross-validation', dest='splits')
# parser.add_argument('-e', '--extra_features', default='',
#     help='Text file (or files separated by spaces) containing extra features (n_sub * n_features) to use', dest='extra')
args = parser.parse_args()

image_sub_list = np.loadtxt(args.image, delimiter=',', dtype=np.int32)
pred_sub_list = np.loadtxt(args.sub_list, delimiter=',', dtype=np.int32)
allDat = np.load(args.data)
path_to_csv = args.pheno
col_to_predict = args.target
n_split = args.splits
savedir = path.dirname(args.output)
savename = path.basename(args.output)

# Don't overwrite current results
if not path.exists(savedir):
    os.makedirs(savedir)
for i in range(100):
    if path.exists(path.join(savedir, savename)):
        savename = savename.replace('.csv', '+.csv')
assert (i < 100), 'Unable to generate filename for output!'

# Handle extra features
if len(args.extra):
    extra_files = args.extra.split()
    for f in extra_files:
        features = np.loadtxt(f)
        allDat = np.hstack([allDat, features])

if col_to_predict == '20016-2.0':
    targetType = 'Fluid intelligence'
elif col_to_predict == '20016_Mean':
    targetType = 'Mean fluid intelligence'
elif col_to_predict == '20127-0.0':
    targetType = 'Neuroticism'
elif col_to_predict == '20127_Mean':
    targetType = 'Mean neuroticism'
elif col_to_predict == '21003-2.0':
    targetType = 'Age'

ukbb = pd.read_csv(path_to_csv, sep='\t', usecols=[col_to_predict, 'eid'])
y = ukbb[['eid', col_to_predict]].dropna()
new_ukbb = pd.DataFrame(ukbb, index=y.index)

# Random splitting of data to train our model
X_train, X_test, y_train, y_test = train_test_split(
    new_ukbb, y, test_size=0.5, random_state=1)


def load_combine_data(X_split):
    data_frame = []
    connectomes = []
    eids = []
    for e_id in X_split.eid:
        this_eid_data = X_split[X_split['eid'] == e_id]
        this_image_ind = np.nonzero(image_sub_list == e_id)[0]
        if np.any(pred_sub_list == e_id):
            eids.append(e_id)
            data_frame.append(this_eid_data)
            connectomes.append(allDat[this_image_ind[0], :])

    X_split = pd.concat(data_frame)
    y_split = pd.DataFrame(X_split, columns=[col_to_predict])

    X_split = X_split.drop(columns=['eid', col_to_predict], axis=1)

    connectomes = pd.DataFrame(connectomes, index=X_split.index)
    return connectomes, y_split


df, y_train = load_combine_data(X_train)

df_test, y_test = load_combine_data(X_test)


estimator = RandomForestClassifier(n_estimators=250, criterion='entropy',
                                  n_jobs=1, verbose=1, random_state=0)


cv = ShuffleSplit(n_splits=n_split, test_size=0.1, random_state=0)

param_grid = {'max_depth': [5, 10, 20, 40, None],
              'max_features': [1, 5, 'log2', 'sqrt', 'auto', None]}
grid_search = GridSearchCV(estimator, param_grid=param_grid,
                           cv=5, verbose=2, n_jobs=int(os.environ['OMP_NUM_THREADS']))

metrics = []
data = []
data_generalization = []

# Add some output
print('')
print('Imaging data file:', args.data)
print('Extra features:', args.extra)
print('Number of features used:', df.shape[1])
print('List of subjects included in analysis:', args.sub_list)
print('Number of subjects after selection:', df.shape[0] + df_test.shape[0])
print('Phenotype file:', args.pheno)
print('Prediction target:', targetType)
print('Training set size:', df.shape[0])
print('Testing set size:', df_test.shape[0])
print('Conducting', n_split, 'fold cross-validation.')
print('Results saved in', path.join(savedir, savename))
print('')

def predict_collect_save(data_pred, data_collect, y_true, test_index,
                         split, save_type):
    scores = {}
    pred_ = grid_search.predict(data_pred)
    y_true_ = y_true.iloc[test_index]
    predictions = pd.DataFrame(pred_, columns=['predicted'],
                               index=y_true_.index)
    predictions['true'] = y_true_
    predictions['test_indices'] = pd.DataFrame(test_index,
                                               columns=['test indices'],
                                               index=y_true_.index)
    predictions['fold'] = pd.Series([split] * len(predictions),
                                    index=predictions.index)
    data_collect.append(predictions)
    scores['mae'] = mean_absolute_error(y_true_, pred_)
    scores['mse'] = mean_squared_error(y_true_, pred_)
    scores['ev'] = explained_variance_score(y_true_, pred_)
    scores['r2_score'] = r2_score(y_true_, pred_)
    scores['fold'] = split
    scores['Estimator'] = 'RandomForest'
    scores['Permuted'] = 'no'
    scores['model_testing'] = save_type
    scores['modality'] = 'functional connectivity (fMRI)'
    scores['target'] = targetType
    metrics.append(scores)
    return


for split, (train_index, test_index) in enumerate(cv.split(df, y_train)):
    scores = {}
    grid_search.fit(df.iloc[train_index], y_train.iloc[train_index].values.ravel())

    predict_collect_save(data_pred=df.iloc[test_index], data_collect=data,
                         y_true=y_train, test_index=test_index,
                         split=split, save_type='validation')

    predict_collect_save(data_pred=df_test, data_collect=data_generalization,
                         y_true=y_test,
                         test_index=np.arange(df_test.shape[0], dtype=np.int),
                         split=split, save_type='generalization')

# save outputs
scores = pd.DataFrame(metrics)
scores.to_csv(path.join(savedir, savename))
