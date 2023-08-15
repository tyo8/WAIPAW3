import seaborn as sns
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# CHANGE THIS:
indir = "/scratch/tyoeasley/WAPIAW3/prediction_outputs"
figout = "/home/l.lexi/prediction_fig/"


brainreplist = ['Demo','T1']
featurelist1 = ['Social']
featurelist2 = ['Volumes', 'Surface']

# create a dataset which represents the concatenated
# contents of a set of results files.
file_list = [file for file in os.listdir(indir) if file.endswith('.csv') & file.startswith('metrics')]
vals = pd.DataFrame()
for i in file_list:
    valset = pd.read_csv(os.path.join(indir, i))
    vals = pd.concat([vals, valset], axis=0)


print(vals)




# REMOVE ANY RESULTS YOU DON"T WANT (OR JUST MAKE SURE
# YOU POINT TO A DIRECTORY THAT ONLY CONTAINS GOOD DATA)
# for example:
# vals = vals.loc[~(vals.group.str.contains("IQ"))].copy()


# This will which will plot any feature in the feature list
# for more options, see http://gree2.github.io/python/2015/05/05/python-seaborn-tutorial-controlling-figure-aesthetics
def plopiwaw_swarm(feats1, feats2, vals=vals, cohort='validation'):
    # vals is Dataframe of concatenated contents of a results files
    # cohort is the variable name of stats group you want to keep
    # list of brain representations
    vals['ptcode'] = vals.group.str.replace("rmed_", "").str.replace("_eid_wapiaw", "")
    vals.sort_values('ptcode', inplace=True)
    subgroup1 = vals.loc[(vals.model_testing == cohort) & (vals.brain_rep == 'Demo')]
    print(subgroup1)
    for i in feats1:
        # stretch out the figure
        fig, ax = plt.subplots(figsize=(18, 10))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.grid(False)
        # create a swarm plot
        sns.swarmplot(data=subgroup1.loc[subgroup1.feature_type == i],
                      x="ptcode",
                      y="accuracy",
                      #y=subgroup1.loc[subgroup1.feature_type == i]["accuracy"].astype(float),
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
                    data=subgroup1.loc[subgroup1.feature_type == i],
                    showfliers=False,
                    showbox=False,
                    showcaps=False)
        plt.xticks(rotation=90, fontsize=14)
        plt.xlabel("")  # "ICD Category of Patient Group")
        plt.ylabel("Accuracy", fontsize=14)
        plt.ylim(0.1, .9)
        plt.title(i, fontsize=18)  # defaults to Brain rep name
        plt.tight_layout()  # neccessary to get the x-axis labels to fit
        plt.axhline(y=0.5, color='lightgrey', linestyle='-', lw=6)
        # plt.axhline(y=0.5, color='grey', linestyle='-',lw=2)
        # plt.axhline(y=0.6, color='lightgrey', linestyle='-',lw=1)
        plt.axhline(y=0.66, color='lightgrey', linestyle='-', lw=1)
        # plt.axhline(y=0.9, color='lightgrey', linestyle='-',lw=1)
        # plt.axhline(y=0.1, color='lightgrey', linestyle='-',lw=1)
        # plt.axhline(y=0.3, color='lightgrey', linestyle='-', lw=1)
        # plt.axhline(y=0.4, color='lightgrey', linestyle='-', lw=1)
        plt.savefig(figout + i + '.png')
    subgroup2 = vals.loc[(vals.model_testing == cohort) & (vals.brain_rep == 'T1')]
    for i in feats2:
        # stretch out the figure
        fig, ax = plt.subplots(figsize=(18, 5))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.grid(False)
        # create a swarm plot
        sns.swarmplot(data=subgroup2.loc[subgroup2.feature_type == i],
                      x="ptcode",
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
                    x="ptcode",
                    y="accuracy",
                    data=subgroup2.loc[subgroup2.feature_type == i],
                    showfliers=False,
                    showbox=False,
                    showcaps=False)
        plt.xticks(rotation=90, fontsize=14)
        plt.xlabel("")  # "ICD Category of Patient Group")
        plt.ylabel("Accuracy", fontsize=14)
        plt.ylim(0.1, .9)
        plt.title(i, fontsize=18)  # defaults to Brain rep name
        plt.tight_layout()  # neccessary to get the x-axis labels to fit
        plt.axhline(y=0.5, color='lightgrey', linestyle='-', lw=6)
        # plt.axhline(y=0.5, color='grey', linestyle='-',lw=2)
        # plt.axhline(y=0.6, color='lightgrey', linestyle='-',lw=1)
        plt.axhline(y=0.66, color='lightgrey', linestyle='-', lw=1)
        # plt.axhline(y=0.9, color='lightgrey', linestyle='-',lw=1)
        # plt.axhline(y=0.1, color='lightgrey', linestyle='-',lw=1)
        # plt.axhline(y=0.3, color='lightgrey', linestyle='-', lw=1)
        # plt.axhline(y=0.4, color='lightgrey', linestyle='-', lw=1)
        plt.savefig(figout + i + '.png')
    plt.show()


# You'll get a lot of warnings about not being able to plot all the points.
# Haven't yet figured out how to make the warnings go away, but they are a function of plot width
plopiwaw_swarm(feats1=featurelist1, feats2=featurelist2)


plt.close()
