import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import warnings

warnings.filterwarnings('ignore')


def get_vals(indir, cohort):  # cohort options: RFC,SVC,age,KNC
    # create a dataset which represents the concatenated
    # contents of a set of results files.
    vals = pd.DataFrame()
    if cohort == 'RFC':
        file_list = [file for file in os.listdir(indir) if
                     file.endswith('.csv') and file.startswith('RFC') and 'age' not in file]
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
        vals['ptcode'] = vals.group.str.replace("age_list_large", "age_large").str.replace("age_list_small",
                                                                                           "age_small")
    elif cohort == 'KNC':
        file_list = [file for file in os.listdir(indir) if
                     file.endswith('.csv') and file.startswith('KNC') and 'age' not in file]
        for i in file_list:
            valset = pd.read_csv(os.path.join(indir, i))
            vals = pd.concat([vals, valset], axis=0)

        # vals['x1']=vals['ptcode']+vals['feature_type']
        # vals['x2']=vals['ptcode']+vals['brain_rep']

    vals = vals[vals['accuracy'] != 'accuracy']
    vals['accuracy'] = vals['accuracy'].astype(float)

    vals['ptcode'] = vals.group.str.replace("rmed_", "").str.replace("_eid_wapiaw", "")
    vals.sort_values('ptcode', inplace=True)
    vals.loc[vals['ptcode'] == 'F0', 'ptgroup'] = 'Organic disorders'
    vals.loc[vals['ptcode'] == 'F10', 'ptgroup'] = 'Alcohol-related disorders'
    vals.loc[vals['ptcode'] == 'F17', 'ptgroup'] = 'Tobacco-related disorders'
    vals.loc[vals['ptcode'] == 'F32', 'ptgroup'] = 'Depression'
    vals.loc[vals['ptcode'] == 'F41', 'ptgroup'] = 'Anxiety (other)'
    vals.loc[vals['ptcode'] == 'G2', 'ptgroup'] = 'Movement disorders'
    vals.loc[vals['ptcode'] == 'G35_37', 'ptgroup'] = 'Demyelinating diseases'
    vals.loc[vals['ptcode'] == 'G40', 'ptgroup'] = 'Epilepsy'
    vals.loc[vals['ptcode'] == 'G43', 'ptgroup'] = 'Migraine'
    vals.loc[vals['ptcode'] == 'G45', 'ptgroup'] = 'Ischaemic attacks'
    vals.loc[vals['ptcode'] == 'G47', 'ptgroup'] = 'Sleep disorders'
    vals.loc[vals['ptcode'] == 'G55', 'ptgroup'] = 'Nerve root compressions'
    vals.loc[vals['ptcode'] == 'G56', 'ptgroup'] = 'Mononeuropathy (upper)'
    vals.loc[vals['ptcode'] == 'G57', 'ptgroup'] = 'Mononeuropathy (lower)'
    vals.loc[vals['ptcode'] == 'G62', 'ptgroup'] = 'Polyneuropathy (other)'
    vals.loc[vals['ptcode'] == 'G8', 'ptgroup'] = 'Paralytic syndromes'
    vals.loc[vals['ptcode'] == 'G93', 'ptgroup'] = 'Other disorders'

    vals.loc[vals['ptcode'] == 'F0', 'size'] = '320'
    vals.loc[vals['ptcode'] == 'F10', 'size'] = '672'
    vals.loc[vals['ptcode'] == 'F17', 'size'] = '1646'
    vals.loc[vals['ptcode'] == 'F32', 'size'] = '2658'
    vals.loc[vals['ptcode'] == 'F41', 'size'] = '2090'
    vals.loc[vals['ptcode'] == 'G2', 'size'] = '384'
    vals.loc[vals['ptcode'] == 'G35_37', 'size'] = '250'
    vals.loc[vals['ptcode'] == 'G40', 'size'] = '478'
    vals.loc[vals['ptcode'] == 'G43', 'size'] = '1042'
    vals.loc[vals['ptcode'] == 'G45', 'size'] = '552'
    vals.loc[vals['ptcode'] == 'G47', 'size'] = '1194'
    vals.loc[vals['ptcode'] == 'G55', 'size'] = '964'
    vals.loc[vals['ptcode'] == 'G56', 'size'] = '1962'
    vals.loc[vals['ptcode'] == 'G57', 'size'] = '386'
    vals.loc[vals['ptcode'] == 'G62', 'size'] = '314'
    vals.loc[vals['ptcode'] == 'G8', 'size'] = '316'
    vals.loc[vals['ptcode'] == 'G93', 'size'] = '296'
    vals.loc[vals['ptcode'] == 'age_large', 'size'] = '2676'
    vals.loc[vals['ptcode'] == 'age_small', 'size'] = '252'

    return vals


# for more options, see http://gree2.github.io/python/2015/05/05/python-seaborn-tutorial-controlling-figure-aesthetics
def plopiwaw_swarm_gray(subgroup):
    # vals is Dataframe of concatenated contents of a results files
    # cohort is the variable name of stats groups you want to keep
    # list of brain representations
    # subgroup = vals.loc[(vals.brain_rep == brainrep) & (vals.feature_type == feat)]
    # create a swarm plot
    sns.swarmplot(data=subgroup,
                  x="ptgroup",
                  y="accuracy",
                  size=6,
                  color="gray",
                  # hue="ptcode",  # trick swarm to plot different colors for groups
                  legend=False,  # turn this back on if you want to get rid of xlabel altogether
                  ax=ax)
    meanpointprops = dict(marker='D', markeredgecolor='black',
                          markerfacecolor='black', markersize=20)
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
    plt.yticks(fontsize=20)
    plt.xlabel("")  # "ICD Category of Patient Group")
    plt.ylabel("Accuracy", fontsize=28)
    plt.ylim(0.1, 1)
    # plt.title(feat, fontsize=18)  # defaults to Brain rep name
    plt.tight_layout()  # neccessary to get the x-axis labels to fit
    # plt.axhline(y=0.66, color='lightgrey', linestyle='-', lw=1)


# def plopiwaw_swarm(brainrep, feat, vals):
def plopiwaw_swarm(subgroup):
    # vals is Dataframe of concatenated contents of a results files
    # cohort is the variable name of stats groups you want to keep
    # list of brain representations
    # subgroup = vals.loc[(vals.brain_rep == brainrep) & (vals.feature_type == feat)]
    # create a swarm plot
    sns.swarmplot(data=subgroup,
                  x="ptgroup",
                  y="accuracy",
                  size=10,
                  hue="ptgroup",  # trick swarm to plot different colors for groups
                  legend=False,  # turn this back on if you want to get rid of xlabel altogether
                  ax=ax)
    meanpointprops = dict(marker='D', markeredgecolor='firebrick',
                          markerfacecolor='firebrick', markersize=20)
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
    plt.xticks(rotation=45, fontsize=50, ha='right')
    plt.yticks(fontsize=50)
    plt.xlabel("")  # "ICD Category of Patient Group")
    plt.ylabel("Accuracy", fontsize=50)
    plt.ylim(0.1, 1)
    # plt.title(brainrep+'_'+feat, fontsize=18)  # defaults to Brain rep name
    plt.tight_layout()  # neccessary to get the x-axis labels to fit
    plt.axhline(y=0.5, color='lightgrey', linestyle='-', lw=8)


if __name__ == "__main__":
    # Figure1:Diagnostic classification based on volumes-based structural neuroimaging features(size not corrected)####
    indir = "/Users/yuanyuanxiaowang/Desktop/prediction_outputs"
    val = get_vals(indir, 'RFC')
    val = val[(val['brain_rep'] == 'T1') & (val['feature_type'] == 'Surface')]
    fig, ax = plt.subplots(figsize=(50, 30))  # stretch out the figure
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.grid(False)
    plopiwaw_swarm(val)
    for k, group in enumerate(val['ptcode'].unique()):
        n = val[val['ptcode'] == group]['size'].max()
        text = 'n=' + n
        plt.text(k, 0.15, text, ha='center', va='bottom', fontsize=45)
    # plt.title('Diagnostic classification based on volumes-based structural neuroimaging features', fontsize=50, y=0.98)
    # plt.show()
    plt.savefig('/Users/yuanyuanxiaowang/Desktop/Figure1_Diagnostic classification based on surface-based structural '
                'neuroimaging features.png')

    # Figure2:size corrected combined figure####
    fig = plt.figure(figsize=(40, 20))
    gs = GridSpec(1, 2, width_ratios=[5, 4])
    # first subplot
    ax1 = fig.add_subplot(gs[0])

    filelist = [file for file in
                os.listdir("/Users/yuanyuanxiaowang/PycharmProjects/pythonProject/WAPIAW/resubmit/prediction_outputs")
                if
                file.endswith('.csv')]
    vals = pd.DataFrame()
    for i in filelist:
        valset = pd.read_csv(
            os.path.join("/Users/yuanyuanxiaowang/PycharmProjects/pythonProject/WAPIAW/resubmit/prediction_outputs", i))
        vals = pd.concat([vals, valset], axis=0)

    val = fix_ptcode(vals)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(True)
    ax1.grid(False)
    plopiwaw_swarm(val, ax1)
    for k, group in enumerate(val['ptcode'].unique()):
        n = val[val['ptcode'] == group]['size'].max()
        text = 'n=' + n
        plt.text(k, 0.15, text, ha='center', va='bottom', fontsize=18)
    # plt.title('Diagnostic classification based on volumes-based structural neuroimaging features', fontsize=30, y=1.1)

    # second subplot
    ax2 = fig.add_subplot(gs[1])
    label_set = ['Organic disorders',
                 'Alcohol-related disorders',
                 'Tobacco-related disorders', 'Depression',
                 'Anxiety (other)',
                 'Movement disorders',
                 'Demyelinating diseases', 'Epilepsy', 'Migraine',
                 'Ischaemic attacks',
                 'Sleep disorders', 'Nerve root compressions',
                 'Mononeuropathy (upper)', 'Mononeuropathy (lower)', 'Polyneuropathy (other)',
                 'Paralytic syndromes', 'Other disorders', 'Healthy']
    indices, labels = pd.factorize(label_set)

    #############
    results = pd.read_csv(
        "/Users/yuanyuanxiaowang/PycharmProjects/pythonProject/WAPIAW/resubmit/resample_T1_Surface.csv", header=None)
    Y_all = results[0]
    y_pred = results[1]
    cm = confusion_matrix(Y_all, y_pred)

    ############
    sns.heatmap(cm, annot=True, ax=ax2, fmt='g', annot_kws={"size": 20})
    ax2.set_xlabel('Predicted', fontsize=30)
    ax2.set_ylabel('True', fontsize=30)
    ax2.set_xticklabels(labels, rotation=45, fontsize=25, ha='right')
    ax2.set_yticklabels(labels, rotation=0, fontsize=25)
    cbar = ax2.collections[0].colorbar
    cbar.ax.tick_params(labelsize=25)
    # ax2.set_title('Multiclass diagnostic classification', fontsize=30, y=1.1)

    # add text
    ax1.text(-0.1, 1.01, '(a)', transform=ax1.transAxes, size=40)
    ax2.text(-0.1, 1.01, '(b)', transform=ax2.transAxes, size=40)

    plt.tight_layout()
    # plt.show()
    plt.savefig('/Users/yuanyuanxiaowang/Desktop/Figure2:size corrected classification&multiclass.png')

    # Figure3: effect of classification models
    indir = "/Users/yuanyuanxiaowang/Desktop/prediction_outputs"
    df = get_vals(indir, 'SVC')
    df1 = get_vals(indir, 'RFC')
    df2 = get_vals(indir, 'KNC')
    df['clf'] = 'SVC'
    df1['clf'] = 'RFC'
    df2['clf'] = 'KNC'

    vals = pd.concat([df, df1, df2], axis=0)
    vals = vals.loc[(vals['brain_rep'].isin(['T1'])) & (vals['feature_type'].isin(['Surface']))]

    vals.sort_values('ptcode', inplace=True)

    ####find best
    vals['combo'] = vals['clf']
    code_list = ['F0', 'F10', 'F17', 'F32', 'F41', 'G2', 'G40', 'G43', 'G45', 'G47', 'G55', 'G56', 'G57', 'G62', 'G8',
                 'G93', 'G35_37']
    vals_best = pd.DataFrame()
    result_df = pd.DataFrame(columns=['code', 'max_accuracy_group'])
    for code in code_list:
        subgroup = vals.loc[vals.ptcode == code]
        # unique_values = subgroup['brainrep_feature'].unique()
        group_accuracies = subgroup.groupby('clf')['accuracy'].mean()
        max_accuracy_group = group_accuracies.idxmax()
        print(code)
        print(max_accuracy_group)
        result_df = result_df.append({'code': code, 'max_accuracy_group': max_accuracy_group}, ignore_index=True)
        df = subgroup.loc[subgroup.clf == max_accuracy_group]
        vals_best = pd.concat([vals_best, df], axis=0)

    vals_best_all = vals_best
    vals_best_all.sort_values('ptcode', inplace=True)

    fig, ax = plt.subplots(figsize=(50, 30))  # stretch out the figure
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.grid(False)
    plopiwaw_swarm_gray(vals)
    plopiwaw_swarm(vals_best_all)
    for k, group in enumerate(vals_best_all['ptcode'].unique()):
        filtered_group = result_df[result_df['code'] == group]['max_accuracy_group']
        print(filtered_group)
        if not filtered_group.empty:
            n = filtered_group.iloc[0]
            size = vals[vals['ptcode'] == group]['size'].max()
            text = 'n=' + size
            print(n)
            plt.text(k, 0.2, n, ha='center', va='bottom', fontsize=45)  # structure/function
            plt.text(k, 0.15, text, ha='center', va='bottom', fontsize=45)
        else:
            # Handle the case where there's no match, if necessary
            pass

    # plt.title('Effect of classification model', fontsize=50, y=0.98)
    figout = "/Users/yuanyuanxiaowang/Desktop"
    plt.show()
    # plt.savefig(os.path.join(figout, 'Figure3_Effect of classification model.png'))

    # Figure4:diagnostic and age classification across feature sets
    vals_icd = get_vals(indir, 'RFC')
    vals_icd = vals_icd.loc[
        vals_icd.brain_rep.isin(['Schaefer', 'ICA25', 'ICA100', 'ICA150', 'ICA300', 'PROFUMO', 'T1', 'Demo'])]
    vals_icd['brain_rep'] = vals_icd['brain_rep'].replace('Demo', 'SocialDemographic')
    vals_age = get_vals(indir, 'age')
    vals_age['ptgroup'] = vals_age.group.str.replace("age_list_large", "age(large)").str.replace("age_list_small",
                                                                                                 "age(small)")

    vals = pd.concat([vals_icd, vals_age], axis=0)

    vals.sort_values('ptcode', inplace=True)

    # find best brainrep within group
    code_list = ['F0', 'F10', 'F17', 'F32', 'F41', 'G2', 'G40', 'G43', 'G45', 'G47', 'G55', 'G56', 'G57', 'G62', 'G8',
                 'G93', 'G35_37']
    vals_best = pd.DataFrame()
    result_df = pd.DataFrame(columns=['code', 'max_accuracy_group'])
    for code in code_list:
        subgroup = vals_icd.loc[vals_icd.ptcode == code]
        subgroup['brainrepfeature'] = subgroup['brain_rep'] + subgroup['feature_type']
        # unique_values = subgroup['brainrep_feature'].unique()
        group_accuracies = subgroup.groupby('brainrepfeature')['accuracy'].mean()
        max_accuracy_group = group_accuracies.idxmax()
        print(code)
        print(max_accuracy_group)
        result_df = result_df.append({'code': code, 'max_accuracy_group': max_accuracy_group}, ignore_index=True)
        df = subgroup.loc[subgroup.brainrepfeature == max_accuracy_group]
        vals_best = pd.concat([vals_best, df], axis=0)

    vals_age = get_vals(indir, 'age')
    vals_age['ptgroup'] = vals_age.group.str.replace("age_list_large", "age(large)").str.replace("age_list_small",
                                                                                                 "age(small)")
    vals_age['ptcode'] = vals_age.group.str.replace("age_list_large", "age(large)").str.replace("age_list_small",
                                                                                                "age(small)")

    vals_best_age = pd.DataFrame()
    age_group = ['age(large)', 'age(small)']
    for code in age_group:
        subgroup = vals_age.loc[vals_age.ptgroup == code]
        subgroup['brainrepfeature'] = subgroup['brain_rep'] + subgroup['feature_type']
        # unique_values = subgroup['brainrep_feature'].unique()
        group_accuracies = subgroup.groupby('brainrepfeature')['accuracy'].mean()
        max_accuracy_group = group_accuracies.idxmax()
        print(code)
        print(max_accuracy_group)
        result_df = result_df.append({'code': code, 'max_accuracy_group': max_accuracy_group}, ignore_index=True)
        df = subgroup.loc[subgroup.brainrepfeature == max_accuracy_group]
        vals_best_age = pd.concat([vals_best_age, df], axis=0)

    vals_best_all = pd.concat([vals_best, vals_best_age], axis=0)
    conditions = [
        vals_best_all['brain_rep'] == 'T1',
        vals_best_all['brain_rep'] == 'SocialDemographic'
    ]
    choices = ['Structural', 'Behavioral']
    vals_best_all['level1'] = np.select(conditions, choices, default='Functional')
    # vals_best_all['ptgroup'] = vals_best_all['ptgroup'] + '(' + 'n=' + vals_best_all['size'] + ')'
    vals_best_all.sort_values('ptcode', inplace=True)

    fig, ax = plt.subplots(figsize=(50, 30))  # stretch out the figure
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.grid(False)
    plopiwaw_swarm_gray(vals)
    plopiwaw_swarm(vals_best_all)
    for k, group in enumerate(vals['ptcode'].unique()):
        n = vals[vals['ptcode'] == group]['size'].max()
        print(n)
        text = 'n=' + n
        plt.text(k, 0.15, text, ha='center', va='bottom', fontsize=40)
    plt.xticks(rotation=45, fontsize=50, ha='right')
    plt.yticks(fontsize=50)
    plt.xlabel("")  # "ICD Category of Patient Group")
    plt.ylabel("Accuracy", fontsize=50)
    plt.ylim(0.1, 1)
    # plt.title(brainrep+'_'+feat, fontsize=18)  # defaults to Brain rep name
    plt.tight_layout()  # neccessary to get the x-axis labels to fit
    plt.axhline(y=0.5, color='lightgrey', linestyle='-', lw=10)
    # plt.title('Diagnostic and age classification across feature sets', fontsize=50, y=0.98)
    # plt.show()
    plt.savefig(os.path.join('/Users/yuanyuanxiaowang/Desktop',
                             'Figure4_Diagnostic and age classification across feature sets.png'))



