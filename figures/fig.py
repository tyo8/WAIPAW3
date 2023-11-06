import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def get_vals(indir, cohort):  # cohort options: RFC,SVC,age
    # create a dataset which represents the concatenated
    # contents of a set of results files.
    vals = pd.DataFrame()
    if cohort == 'RFC':
        file_list = [file for file in os.listdir(indir) if
                     file.endswith('.csv') and file.startswith('metrics') and 'age' not in file]
        for i in file_list:
            valset = pd.read_csv(os.path.join(indir, i))
            vals = pd.concat([vals, valset], axis=0)
    elif cohort == 'SVC':
        file_list = [file for file in os.listdir(indir) if
                     file.endswith('.csv') and file.startswith('SVC') and 'age' not in file]
        for i in file_list:
            valset = pd.read_csv(os.path.join(indir, i))
            vals = pd.concat([vals, valset], axis=0)
    elif cohort == 'age':
        file_list = [file for file in os.listdir(indir) if file.endswith('.csv') and 'age' in file]
        for i in file_list:
            valset = pd.read_csv(os.path.join(indir, i))
            vals = pd.concat([vals, valset], axis=0)
        vals['ptcode'] = vals.group.str.replace("age_list_large", "large").str.replace("age_list_small", "small")
        # vals['x1']=vals['ptcode']+vals['feature_type']
        # vals['x2']=vals['ptcode']+vals['brain_rep']

    vals['ptcode'] = vals.group.str.replace("rmed_", "").str.replace("_eid_wapiaw", "")
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

    return vals


# for more options, see http://gree2.github.io/python/2015/05/05/python-seaborn-tutorial-controlling-figure-aesthetics
def plopiwaw_swarm_gray(brainrep, feat, vals):
    # vals is Dataframe of concatenated contents of a results files
    # cohort is the variable name of stats groups you want to keep
    # list of brain representations
    subgroup = vals.loc[(vals.brain_rep == brainrep) & (vals.feature_type == feat)]
    # create a swarm plot
    sns.swarmplot(data=subgroup,
                  x="ptgroup",
                  y="accuracy",
                  size=5,
                  color="gray",
                  # hue="ptcode",  # trick swarm to plot different colors for groups
                  legend=False,  # turn this back on if you want to get rid of xlabel altogether
                  ax=ax)
    meanpointprops = dict(marker='D', markeredgecolor='black',
                          markerfacecolor='black')
    # adding a boxplot where everything is invisible except the mean
    sns.boxplot(showmeans=True,
                meanline=False,
                meanprops=meanpointprops,
                medianprops={'visible': False},
                whiskerprops={'visible': False},
                zorder=10,
                x="ptgroup",
                y="accuracy",
                data=subgroup,
                showfliers=False,
                showbox=False,
                showcaps=False)
    plt.xticks(rotation=45, fontsize=18, ha='right')
    plt.xlabel("")  # "ICD Category of Patient Group")
    plt.ylabel("Accuracy", fontsize=14)
    plt.ylim(0.1, 1)
    plt.title(brainrep, fontsize=18)  # defaults to Brain rep name
    plt.tight_layout()  # neccessary to get the x-axis labels to fit
    # plt.axhline(y=0.66, color='lightgrey', linestyle='-', lw=1)


def plopiwaw_swarm(brainrep, feat, vals):
    # vals is Dataframe of concatenated contents of a results files
    # cohort is the variable name of stats groups you want to keep
    # list of brain representations
    subgroup = vals.loc[(vals.brain_rep == brainrep) & (vals.feature_type == feat)]
    # create a swarm plot
    sns.swarmplot(data=subgroup,
                  x="ptgroup",
                  y="accuracy",
                  size=5,
                  hue="ptcode",  # trick swarm to plot different colors for groups
                  legend=False,  # turn this back on if you want to get rid of xlabel altogether
                  ax=ax)
    meanpointprops = dict(marker='D', markeredgecolor='firebrick',
                          markerfacecolor='firebrick')
    # adding a boxplot where everything is invisible except the mean
    sns.boxplot(showmeans=True,
                meanline=False,
                meanprops=meanpointprops,
                medianprops={'visible': False},
                whiskerprops={'visible': False},
                zorder=10,
                x="ptgroup",
                y="accuracy",
                data=subgroup,
                showfliers=False,
                showbox=False,
                showcaps=False)
    plt.xticks(rotation=45, fontsize=18, ha='right')
    plt.xlabel("")  # "ICD Category of Patient Group")
    plt.ylabel("Accuracy", fontsize=14)
    plt.ylim(0.1, 1)
    plt.title(brainrep, fontsize=18)  # defaults to Brain rep name
    plt.tight_layout()  # neccessary to get the x-axis labels to fit
    # plt.axhline(y=0.66, color='lightgrey', linestyle='-', lw=1)


def add_size(brainrep, feat, vals):
    vals['size'] = None
    label_list = '/scratch/tyoeasley/WAPIAW3/figures/codelist.txt'
    with open(label_list, 'r') as fin:
        labels = fin.read().split()
    for i in labels:
        files = f"/scratch/tyoeasley/WAPIAW3/subject_lists/combined_subj_eid/rmed_{i}_eid_wapiaw.csv"
        with open(files, 'r') as fin:
            vals.loc[vals['ptcode'] == i, 'size'] = len(fin.read().split())
    subgroup = vals.loc[(vals.brain_rep == brainrep) & (vals.feature_type == feat)]
    y_text_position = 0.15
    for k, group in enumerate(subgroup['ptcode'].unique()):
        n = subgroup[subgroup['ptcode'] == group]['size'].max()
        plt.text(k, y_text_position, n, ha='center', va='bottom')


if __name__ == "__main__":
    # CHANGE THIS:
    indir = "/scratch/tyoeasley/WAPIAW3/prediction_outputs"
    figout = "/scratch/tyoeasley/WAPIAW3/figures/swarm_fig/"
    # brainreplist = ['ICA25', 'ICA100', 'ICA150', 'ICA300', 'Schaefer', 'Demo']
    brainreplist = ['ICA300']
    # featurelist = ['Social']
    featurelist = ['Amplitudes', 'NetMats', 'partial_NMs']

    vals = get_vals(indir, 'RFC')
    for i in brainreplist:
        for j in featurelist:
            fig, ax = plt.subplots(figsize=(30, 20))  # stretch out the figure
            # plopiwaw_swarm_gray('Demo', 'Social', vals)
            plopiwaw_swarm(i, j, vals)
            add_size(i, j, vals)
            plt.savefig(figout + i + '_' + j + '.png')
    plt.close()
