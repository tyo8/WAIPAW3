import os
import ast
import warnings
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="do heatmap")
    parser.add_argument(
        '-m',
        '--metrics_dir',
        type=str,
        default="/Users/yuanyuanxiaowang/Desktop/metrics",
        help='dir to read metrics'
    )
    parser.add_argument(
        '-b',
        '--brainrep_flist',
        type=str,
        default=["T1_Volumes"],
        help="brain representation list"
    )
    parser.add_argument(
        '-c',
        '--code_flist',
        type=str,
        default=["G8", "G57", "G62"],
        help="brain representation list"
    )
    parser.add_argument(
        '-s',
        '--save_dir',
        type=str,
        default="/scratch/tyoeasley/WAPIAW3/cross-prediction_outputs/figures",
        help="where to save the figures"
    )

args = parser.parse_args()

#code_list = ast.literal_eval(args.code_list)
#brainrep_list = ast.literal_eval(args.brainrep_list)
with open(args.code_flist, 'r') as fin:    
    code_list=fin.read().split()
with open(args.brainrep_flist, 'r') as fin:    
    brainrep_list=fin.read().split()

metrics_dir = "/scratch/tyoeasley/WAPIAW3/cross-prediction_outputs"
save_dir = "/scratch/tyoeasley/WAPIAW3/cross-prediction_outputs/figures"
print(code_list)
print(brainrep_list)
counter =0
n=len(code_list)
for brainrep in brainrep_list:
    avg_all = pd.DataFrame()
    for file1 in code_list:
        for file2 in code_list:
            counter = counter +1
            if file1 != file2:
                filename = "metrics_rmed_%s_eid_wapiaw_from_rmed_%s_eid_wapiaw_%s.csv" % (file1, file2, brainrep)
                #filename = "metrics_rmed_" + file1 + "_eid_wapiaw_from_rmed_" + file2 + "_eid_wapiaw_" + brainrep + ".csv"
                accuracy = pd.read_csv(os.path.join(metrics_dir, filename), dtype=float, usecols=[1], index_col=None,
                                       header=0)
                file = "%s_from_%s" % (file1, file2)
                avg = accuracy.mean()
                avg = avg.to_frame(name="header")
                avg = avg.iloc[0, 0]
                avg_all = avg_all.append(pd.DataFrame({'name': [file], 'mean': [avg]}), ignore_index=True)
                print(avg)
            else:
                avg = 1
                file = "%s_from_%s" % (file1, file2)
                avg_all = avg_all.append(pd.DataFrame({'name': [file], 'mean': [avg]}), ignore_index=True)

    print(avg_all)
    df = pd.DataFrame(avg_all['mean'].values.reshape(n, n), columns=code_list, index=code_list)
    np.fill_diagonal(df.values, np.nan)

    print(df)
    cmap = sns.cm.rocket_r
    cmap.set_bad(color='gray')
    ax = sns.heatmap(df, linewidth=0.5, cmap=cmap, vmin=0.4, vmax=1)
    plt.title(brainrep_list[0])
    plt.xlabel("Generated from")
    plt.ylabel("Predicted on")
    fig_name = brainrep + "_heatmap.png"
    plt.savefig(fig_name)
    plt.close()

print(counter)
