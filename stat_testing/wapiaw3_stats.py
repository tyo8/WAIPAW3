import os
import warnings
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from scipy import stats
from decimal import Decimal

warnings.filterwarnings('ignore')

# default variable values (defined as global variables)
def_brainreps = ['Schaefer', 'ICA25', 'ICA100', 'ICA150', 'ICA300', 'PROFUMO', 'T1', 'Demo']
T1_only = ['T1']
def_codes = ['F0', 'F10', 'F17', 'F32', 'F41', 'G2', 'G40', 'G43', 'G45', 'G47', 'G55', 'G56', 'G57', 'G62', 'G8',
                 'G93', 'G35_37', 'age_large', 'age_small']

def get_vals(indir, results_subtype, separate_age=False):  
    # results_subtype options: RFC,SVC,KNC,age
    # create a dataset which represents the concatenated
    # contents of a set of results filenames.

    vals = pd.DataFrame()

    if results_subtype == 'age':
        filename_list = [filename for filename in os.listdir(indir) if 
                filename.endswith('.csv') and 'age' in filename]
    elif separate_age:
        filename_list = [filename for filename in os.listdir(indir) if
                filename.endswith('.csv') and filename.startswith(results_subtype) and 'age' not in filename]
    else:
        filename_list = [filename for filename in os.listdir(indir) if
                filename.endswith('.csv') and filename.startswith(results_subtype)]
        ### debugging code ###
        # print([filename for filename in filename_list if 'age' in filename])
        ### debugging code ###

    for i in filename_list:
        valset = pd.read_csv(os.path.join(indir, i))
        vals = pd.concat([vals, valset], axis=0)

    vals['ptcode'] = vals.group.str.replace("rmed_", "").str.replace("_eid_wapiaw", "").str.replace("age_list_", "age_")

    ### debugging code ###
    # print("Unique code values after string replacement: ", vals['ptcode'].unique())
    ### debugging code ###

        # vals['x1']=vals['ptcode']+vals['feature_type']
        # vals['x2']=vals['ptcode']+vals['brain_rep']

    vals = vals[vals['accuracy'] != 'accuracy']
    vals['accuracy'] = vals['accuracy'].astype(float)

    vals.sort_values('ptcode', inplace=True)
    vals.loc[vals['ptcode'] == 'F0', 'ptgroup'] = 'Organic, including symptomatic, mental disorders'
    vals.loc[vals['ptcode'] == 'F10', 'ptgroup'] = 'Mental and behavioural disorders due to use of alcohol'
    vals.loc[vals['ptcode'] == 'F17', 'ptgroup'] = 'Mental and behavioural disorders due to use of tobacco'
    vals.loc[vals['ptcode'] == 'F32', 'ptgroup'] = 'Depressive episode'
    vals.loc[vals['ptcode'] == 'F41', 'ptgroup'] = 'Other anxiety disorders'
    vals.loc[vals['ptcode'] == 'G2', 'ptgroup'] = 'Extrapyramidal and movement disorders (parkinson)'
    vals.loc[vals['ptcode'] == 'G35_37', 'ptgroup'] = 'Demyelinating diseases of the central nervous systems'
    vals.loc[vals['ptcode'] == 'G40', 'ptgroup'] = 'Epilepsy'
    vals.loc[vals['ptcode'] == 'G43', 'ptgroup'] = 'Migraine'
    vals.loc[vals['ptcode'] == 'G45', 'ptgroup'] = 'Transient cerebral ischaemic attacks and related syndromes'
    vals.loc[vals['ptcode'] == 'G47', 'ptgroup'] = 'Sleep disorders'
    vals.loc[vals['ptcode'] == 'G55', 'ptgroup'] = 'Nerve root and plexus compressions in diseases classified elsewhere'
    vals.loc[vals['ptcode'] == 'G56', 'ptgroup'] = 'Mononeuropathies of upper limb'
    vals.loc[vals['ptcode'] == 'G57', 'ptgroup'] = 'Mononeuropathies of lower limb'
    vals.loc[vals['ptcode'] == 'G62', 'ptgroup'] = 'Other polyneuropathies'
    vals.loc[vals['ptcode'] == 'G8', 'ptgroup'] = 'Cerebral Palsy and other paralytic syndroms'
    vals.loc[vals['ptcode'] == 'G93', 'ptgroup'] = 'Other disorders of brain'
    vals.loc[vals['ptcode'] == 'age_large', 'ptgroup'] = 'Large group of age-stratified subjects'
    vals.loc[vals['ptcode'] == 'age_small', 'ptgroup'] = 'Subsample of age-stratified subjects'

    return vals


# find best brainrep within group
def best_brainrep(vals_all, brainrep_list=def_brainreps, code_list=def_codes, 
        results_subtype='RFC', separate_age=False, verbose=True):
        

    vals_all = vals_all.loc[vals_all.brain_rep.isin(brainrep_list)]

    vals_best = pd.DataFrame()
    result_df = pd.DataFrame(columns=['code', 'max_accuracy_group'])

    ### debugging code ###
    # print("Code value set in \'best_brainrep\' check: ", vals_all.ptcode.unique())
    ### debugging code ###

    for code in code_list:
        subgroup = vals_all.loc[vals_all.ptcode == code]
        subgroup['brainrepfeature'] = subgroup['brain_rep'] + subgroup['feature_type']
        unique_values = subgroup['brainrepfeature'].unique()
        unique_values.sort()

        if verbose:
            print(f"\nDiagnostic code \"{code}\" was predicted using {len(unique_values)} distinct choices of feature set.")

        group_means = subgroup.groupby('brainrepfeature')['accuracy'].mean()
        group_std = subgroup.groupby('brainrepfeature')['accuracy'].std()
        group_degfree = subgroup.groupby('brainrepfeature')['accuracy'].size()-1
        group_pvals, group_uncorr_pvals = sig_testing(group_means, group_std, group_degfree, verbose=False) 

        ### debugging code ###
        # print(f"We record {len(subgroup)} group accuracy observations per feature in diagnostic group \"{code}\".")
        # print(f"Means (type {type(group_means)}):")
        # print(group_means)
        # print(subgroup)
        ### debugging code ###

        if min(group_pvals == 1):
            sig_accuracy_group = group_means.index[np.argmin(group_uncorr_pvals)]
        else:
            sig_accuracy_group = group_means.index[np.argmin(group_pvals)]
            if min(group_pvals) < 0.05:
                granular_results_df = pd.DataFrame()
                for i,pval in enumerate(group_pvals):
                    # pval_group = group_means.index[np.argmin(np.abs(group_pvals - pval))]
                    pval_group = group_means.index[i]
                    if pval < 0.05:
                        pval_text = "*" + '%.5E' % Decimal(pval) + "*"
                    elif pval < 0.10:
                        pval_text = "~" + '%.5E' % Decimal(pval) + "~"
                    else:
                        pval_text = '%.5E' % Decimal(pval)

                    granular_results_df = granular_results_df._append({
                        'group': pval_group,
                        'best_corr_pval': pval_text,
                        }, ignore_index=True)

                    for j in range(i+1,len(group_pvals)):
                        n_compare = len(group_pvals)**2 - len(group_pvals)
                        group_i = pval_group
                        group_j = group_means.index[j]
                        # pval_ij = sig_testing(group_means[i], group_std[i], group_degfree[i], popmean=group_means[j], verbose=False)
                        pval_ij = stats.ttest_ind(
                                subgroup.loc[subgroup.brainrepfeature == group_i]['accuracy'], 
                                subgroup.loc[subgroup.brainrepfeature == group_j]['accuracy'],
                                equal_var = False).pvalue
                        if pval_ij*n_compare < 0.01:
                            print(f"Feature {group_i} (might) predict significantly higher than feature {group_j} in {code}, with x{n_compare} threshold:     p = {pval_ij*n_compare}")


                print(granular_results_df)
                    
        max_accuracy_group = group_means.idxmax()

        if verbose:
            print(f"Feature \"{sig_accuracy_group}\" gave most significant classification of diagnostic group \"{code}\".")
            print(f"Feature \"{max_accuracy_group}\" gave highest mean classification of diagnostic group \"{code}\".")

        result_df = result_df._append({
            'code': code, 
            'max_accuracy_group': max_accuracy_group,
            'sig_accuracy_group': sig_accuracy_group,
            'max_mean_accuracy': group_means[max_accuracy_group],
            'best_uncorr_pval': min(group_uncorr_pvals),
            'best_corr_pval': min(group_pvals),
            }, ignore_index=True)
        df = subgroup.loc[subgroup.brainrepfeature == max_accuracy_group]
        vals_best = pd.concat([vals_best, df], axis=0)

        ### debugging code ###
        # print(f"\'Best value\' update in group {code} has dimension {df.shape} and looks like:")
        # print(df)
        ### debugging code ###

    vals_best.sort_values('ptgroup', inplace=True)
    if verbose:
        print("Summary of best predictions per diagnostic code group:")
        print(result_df)

    return vals_best, result_df

def sig_testing(means, stds, degfree, popmean=0.5, verbose=True):
    pvals = stats.t.sf((means - popmean)/stds, degfree)
    if verbose:
        print("Family of p-values (before correction):", f" minimum={min(pvals)}")
        print(pvals)

    corr_pvals = stats.false_discovery_control(pvals,method='bh')
    if verbose:
        print("Family of p-values (after correction):", f" minimum={min(corr_pvals)}")
        print(corr_pvals)

    # check for uniqueness
    if isinstance(corr_pvals, list):
        if min(corr_pvals) == 1:
            if verbose:
                print("All p-values are 1 after correction!")

    return corr_pvals, pvals


def sig_testing1(data, n_tests=1):
    print(f"Significance-testing prediction accuracy data in \"{data.ptcode[0]}\" ({data.ptgroup[0]}), which is best predicted by {data.brainrepfeature[0]}")
    print(f"This group has {len(data)} sample retests and corresponding sample mean {np.mean(data.accuracy)}, and gives best accuracy out of {n_tests} choices of feature set predictor")

    # compute p-value of hypothesis that given sample does not predict above chance
    # not that we are NOT computing with the standard error here, since we are *already* looking at a distribution of the sample mean
    pvalue = stats.t.sf((np.mean(data.accuracy)- 0.5)/np.std(data.accuracy), len(data)-1 )

    print(f"This fails to predict above chance with probability p={pvalue} (uncorrected) / p={pvalue*n_tests} (Bonferroni)")



if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Statistical testing for WAPIAW3 predictive classification accuracies")
    parser.add_argument(
            '-i',
            '--indir',
            type=str,
            default='/scratch/tyoeasley/WAPIAW3/prediction_outputs',
            help='directory in which to short for input files'
            )
    parser.add_argument(
            '-r',
            '--results_subtype',
            type=str,
            default="RFC",
            help="subtype of results data to search within"
            )
    parser.add_argument(
            '-a',
            '--separate_age',
            default=False,
            action='store_true',
            help='whether or not to exclude age data from results retrieval'
            )
    parser.add_argument(
            '-B',
            '--brainrep_list',
            type=list,
            default=def_brainreps,
            # default=T1_only,
            help="list of brain representation identifiers"
            )
    parser.add_argument(
            '-C',
            '--code_list',
            type=list,
            default=def_codes,
            help="list of diagnostic code groupings"
            )
    parser.add_argument(
            '-v',
            '--verbose',
            default=False,
            action='store_true',
            help='flag to give verbose output'
            )
    args = parser.parse_args()

    vals_all = get_vals(
            args.indir, 
            args.results_subtype, 
            separate_age=args.separate_age
            )

    vals_best, result_df = best_brainrep(
            vals_all, 
            brainrep_list=args.brainrep_list,
            code_list=args.code_list,
            results_subtype=args.results_subtype, 
            separate_age=args.separate_age
            )

#    sig_testing(
#            vals_all,
#            vals_best,
#            result_df
#            )
