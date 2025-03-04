import seaborn as sns
import os
import ast
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#######################################################################################################################
### TREAT THESE AS DEFAULT VARIABLES OF INPUT PARSER ###
brainreplist = ['Demo', 'ICA300']
featurelist1 = ['Social']
# featurelist2 = ['NetMats', 'spatialNMs'] # PROFUMO
featurelist2 = ['Amplitudes', 'NetMats', 'partial_NMs']  # 'ICA25', 'ICA100', 'ICA150', 'ICA300', 'Schaefer'
# featurelist2 = ['Volumes', 'Surface']  # T1
#######################################################################################################################



#######################################################################################################################
### THIS CAN ALL BE A FUNCTION THAT TAKES ONLY 'indir' AND 'figout' AS INPUTS AND RETURNS 'vals' AS AN OUTPUT (?) ###
# CHANGE THIS:
indir = "/Users/yuanyuanxiaowang/PycharmProjects/pythonProject/WAPIAW/prediction_outputs"
figout = "/Users/yuanyuanxiaowang/Desktop/figout"

# create a dataset which represents the concatenated
# contents of a set of results files.
file_list = [fe for fe in os.listdir(indir) if
             fe.endswith('.csv') and fe.startswith('metrics') and 'age' not in fe]
vals = pd.DataFrame()
for i in file_list:
    valset = pd.read_csv(os.path.join(indir, i))
    vals = pd.concat([vals, valset], axis=0)

vals['ptcode'] = vals.group.str.replace("rmed_", "").str.replace("_eid_wapiaw", "")
vals.sort_values('ptcode', inplace=True)
vals['size'] = None
### CONSIDER CHANGING HARDCODING TO READING NUMBER OF ENTRIES ### (example code below)
# for label in label_list:
#     file = f"/scratch/tyoeasley/WAPIAW3/subject_list/??something??{label}"
#     with open(file, 'r') as fin:
#         vals.loc[vals['ptcode'] == label, 'size'] = len(fin.read.split()
label_list = '/scratch/tyoeasley/WAPIAW3/figures/codelist.txt'
with open(label_list, 'r') as fin:
    labels=fin.read().split()
for i in labels:
    files = f"/scratch/tyoeasley/WAPIAW3/subject_lists/combined_subj_eid_unique/{i}_unique"
    with open(files,'r') as fin:

        vals.loc[vals['ptcode'] == i, 'size'] = len(fin.read.split())


vals.loc[vals['ptcode'] == 'F0', 'ptcode'] = 'Organic, including symptomatic, mental disorders'
vals.loc[vals['ptcode'] == 'F10', 'ptcode'] = 'Mental and behavioural disorders due to use of alcohol'
vals.loc[vals['ptcode'] == 'F17', 'ptcode'] = 'Mental and behavioural disorders due to use of tobacco'
vals.loc[vals['ptcode'] == 'F32', 'ptcode'] = 'Depressive episode'
vals.loc[vals['ptcode'] == 'F41', 'ptcode'] = 'Other anxiety disorders'
vals.loc[vals['ptcode'] == 'G2', 'ptcode'] = 'Extrapyramidal and movement disorders (parkinson)'
vals.loc[vals['ptcode'] == 'G35_37', 'ptcode'] = 'Demyelinating diseases of the central nervous systems'
vals.loc[vals['ptcode'] == 'G40', 'ptcode'] = 'Epilepsy'
vals.loc[vals['ptcode'] == 'G43', 'ptcode'] = 'Migraine'
vals.loc[vals['ptcode'] == 'G45', 'ptcode'] = 'Transient cerebral ischaemic attacks and related syndromes'
vals.loc[vals['ptcode'] == 'G47', 'ptcode'] = 'Sleep disorders'
vals.loc[vals['ptcode'] == 'G55', 'ptcode'] = 'Nerve root and plexus compressions in diseases classified elsewhere'
vals.loc[vals['ptcode'] == 'G56', 'ptcode'] = 'Mononeuropathies of upper limb'
vals.loc[vals['ptcode'] == 'G57', 'ptcode'] = 'Mononeuropathies of lower limb'
vals.loc[vals['ptcode'] == 'G62', 'ptcode'] = 'Other polyneuropathies'
vals.loc[vals['ptcode'] == 'G8', 'ptcode'] = 'Cerebral Palsy and other paralytic syndroms'
vals.loc[vals['ptcode'] == 'G93', 'ptcode'] = 'Other disorders of brain'

# vals['accuracy'] = vals['accuracy'].astype('float')

# REMOVE ANY RESULTS YOU DON"T WANT (OR JUST MAKE SURE
# YOU POINT TO A DIRECTORY THAT ONLY CONTAINS GOOD DATA)
# for example:
# vals = vals.loc[~(vals.group.str.contains("IQ"))].copy()

#######################################################################################################################





# This will which will plot any feature in the feature list
# for more options, see http://gree2.github.io/python/2015/05/05/python-seaborn-tutorial-controlling-figure-aesthetics
def plopiwaw_swarm(feats1, feats2, vals=vals, cohort='validation'):
    # vals is Dataframe of concatenated contents of a results files
    # cohort is the variable name of stats groups you want to keep
    # list of brain representations
    subgroup1 = vals.loc[(vals.model_testing == cohort) & (vals.brain_rep == brainreplist[0])]
    subgroup2 = vals.loc[(vals.model_testing == cohort) & (vals.brain_rep == brainreplist[1])]
    subgroup1.sort_values('ptcode', inplace=True)
    subgroup2.sort_values('ptcode', inplace=True)
    for j in feats2:
        # stretch out the figure
        fig, ax = plt.subplots(figsize=(30, 20))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.grid(False)
        # create a swarm plot

        ###############################################################################################################
        ### CONSOLIDATE INTO A FUNCTION THAT TAKES DATA AS INPUT; CALL AS MANY TIMES AS YOU HAVE SUBGROUPS ###
        sns.swarmplot(data=subgroup2.loc[subgroup2.feature_type == j],
                      x="ptcode",
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
                    x="ptcode",
                    y="accuracy",
                    data=subgroup2.loc[subgroup2.feature_type == j],
                    showfliers=False,
                    showbox=False,
                    showcaps=False)
        ###############################################################################################################

        sns.swarmplot(data=subgroup1.loc[subgroup1.feature_type == feats1[0]],
                      x="ptcode",
                      y="accuracy",
                      # y=subgroup1.loc[subgroup1.feature_type == i]["accuracy"].astype(float),
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
                    x="ptcode",
                    y="accuracy",
                    data=subgroup1.loc[subgroup1.feature_type == feats1[0]],
                    showfliers=False,
                    showbox=False,
                    showcaps=False)
        # adding size for each group
        y_text_position = subgroup1['accuracy'].min() - 0.01
        for i, group in enumerate(subgroup1['ptcode'].unique()):
            n = subgroup1[subgroup1['ptcode'] == group]['size'].max()
            plt.text(i, y_text_position, n, ha='center', va='bottom')
        plt.xticks(rotation=45, fontsize=18, ha='right')
        plt.xlabel("")  # "ICD Category of Patient Group")
        plt.ylabel("Accuracy", fontsize=14)
        plt.ylim(0.25, .9)
        plt.title(j, fontsize=18)  # defaults to Brain rep's feature name in variable "j"
        plt.tight_layout()  # neccessary to get the x-axis labels to fit
        plt.axhline(y=0.66, color='lightgrey', linestyle='-', lw=1)
        
        # plt.savefig(f"{figout}{i}_{brainreplist[1]}_{j}.png")
        plt.savefig('test.png')
        plt.show()
        plt.close()


# You'll get a lot of warnings about not being able to plot all the points.
# Haven't yet figured out how to make the warnings go away, but they are a function of plot width.

if __name__=="__main__":
    ### ADD INPUT PARSER HERE -- WHAT VARIABLES WOULD YOU LIKE TO BE ABLE TO SPECIFY? ###
    plopiwaw_swarm(feats1=featurelist1, feats2=featurelist2)
