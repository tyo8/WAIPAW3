import seaborn as sns
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# CHANGE THIS:
indir = "/Users/yuanyuanxiaowang/PycharmProjects/pythonProject/WAPIAW/prediction_outputs"
figout = "/Users/yuanyuanxiaowang/Desktop/figout/"

#brainreplist = ['ICA25', 'ICA100', 'ICA150', 'ICA300', 'Schaefer']
brainreplist = ['Demo']
featurelist = ['Social']
#featurelist = ['Amplitudes', 'NetMats', 'partial_NMs']

# create a dataset which represents the concatenated
# contents of a set of results files.
#file_list = [file for file in os.listdir(indir) if file.endswith('.csv') and 'age' in file]
file_list = [file for file in os.listdir(indir) if file.endswith('.csv') & file.startswith('metrics')]
vals = pd.DataFrame()
for i in file_list:
    valset = pd.read_csv(os.path.join(indir, i))
    vals = pd.concat([vals, valset], axis=0)

#vals['ptcode'] = vals.group.str.replace("age_list_large", "large").str.replace("age_list_small", "small")
#vals['x1']=vals['ptcode']+vals['feature_type']
#vals['x2']=vals['ptcode']+vals['brain_rep']
vals['ptcode'] = vals.group.str.replace("rmed_", "").str.replace("_eid_wapiaw", "")
vals.sort_values('ptcode', inplace=True)
#vals.sort_values('x2', inplace=True)

print(vals)


# REMOVE ANY RESULTS YOU DON"T WANT (OR JUST MAKE SURE
# YOU POINT TO A DIRECTORY THAT ONLY CONTAINS GOOD DATA)
# for example:
# vals = vals.loc[~(vals.group.str.contains("IQ"))].copy()


# This will which will plot any feature in the feature list
# for more options, see http://gree2.github.io/python/2015/05/05/python-seaborn-tutorial-controlling-figure-aesthetics
def plopiwaw_swarm(feats1, vals=vals, cohort='validation'):
    # vals is Dataframe of concatenated contents of a results files
    # cohort is the variable name of stats groups you want to keep
    # list of brain representations
    for i in featurelist:
        # subgroup = vals.loc[(vals.model_testing == cohort) & (vals.brain_rep == i)]
        subgroup = vals.loc[(vals.model_testing == cohort) & (vals.feature_type == i)]
        fig, ax = plt.subplots(figsize=(18, 10))  # stretch out the figure
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.grid(False)
        # create a swarm plot
        sns.swarmplot(data=subgroup,
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
                    data=subgroup,
                    showfliers=False,
                    showbox=False,
                    showcaps=False)
        plt.xticks(fontsize=14)
        plt.xlabel("")  # "ICD Category of Patient Group")
        plt.ylabel("Accuracy", fontsize=14)
        plt.ylim(0.1, 1)
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
        #plt.savefig(figout + i + '.png')
    plt.show()


# You'll get a lot of warnings about not being able to plot all the points.
# Haven't yet figured out how to make the warnings go away, but they are a function of plot width
plopiwaw_swarm(feats1=featurelist)

plt.close()
