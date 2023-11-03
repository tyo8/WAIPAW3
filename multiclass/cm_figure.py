import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix


def save_figure(cm,labels,brainrep,feature):
    # save the confusion matrix figures
    fig = plt.figure(figsize=(16, 14))
    ax= plt.subplot()
    sns.heatmap(cm, annot=True, ax = ax, fmt = 'g'); #annot=True to annotate cells
    # labels, title and ticks
    ax.set_xlabel('Predicted', fontsize=20)
    ax.xaxis.set_label_position('bottom')
    plt.xticks(rotation=90)
    ax.xaxis.set_ticklabels(labels, fontsize = 10)
    ax.xaxis.tick_bottom()

    ax.set_ylabel('True', fontsize=20)
    ax.yaxis.set_ticklabels(labels, fontsize = 10)
    plt.yticks(rotation=0)
    plt.title(brainrep+"_"+feature, fontsize=20)
    plt.savefig(f"/scratch/tyoeasley/WAPIAW3/multiclass/confusion_matrix/{brainrep}_{feature}_confusion_metrics.png")

# debugging function to understand confusion matrix:
def inspect_cm(cm, labels):
    import numpy as np
    rowsum = np.sum(cm, axis=1)
    colsum = np.sum(cm, axis=0)

    true_pos = np.diag(cm)
    true_neg = colsum + rowsum - 2*np.diag(cm)
    false_pos = colsum - np.diag(cm)
    false_neg = rowsum - np.diag(cm)
    TPR = true_pos / rowsum
    TNR = true_neg / (true_neg + false_pos)

    stats_summary = pd.DataFrame({
        "Sensitivity": TPR,
        "Specificity": TNR,
        "#true_pos": true_pos,
        "#true_neg": true_neg,
        "#false_pos": false_pos,
        "#false_neg": false_neg,
        "proportion of sample in class": rowsum/sum(rowsum),
        "proportion of predictions in class": colsum/(sum(colsum))
        }, index=labels)
    print("Precision summary of confusion matrix:")
    print(stats_summary)

    stats_summary.drop(
            # columns=["Sensitivity", "Specificity", "#true_pos", "#false_pos", "#true_neg", "#false_neg"], 
            index="Other disorders",
            inplace=True)
    x = rowsum[colsum > 0]
    y = colsum[colsum > 0]
    from scipy.stats import linregress 
    result = linregress(x, np.log10(y))
    print(f"Association strength of subject number and log(prediction proportion): R^2 = {result.rvalue**2}. Further details below.")
    print(result)


    fig, ax = plt.subplots()
    stats_summary.plot( "proportion of sample in class", "proportion of predictions in class", kind="scatter", ax=ax)
    ax.set_yscale("log")
    plt.title("Classification likelihood as a function of class size")
#    for i, data in stats_summary.iterrows():
#        if "Demy" in i or "Health" in i:
#            plt.annotate(i, data, ha='left', rotation=0)

    fig, ax = plt.subplots()
    stats_summary.plot( "proportion of sample in class", "Sensitivity", kind="scatter", ax=ax)
    plt.title("True positive rate as a function of class size")
    plt.savefig("sampsize_vs_TPR.png",dpi=600)

if __name__=="__main__":
    brainrep=sys.argv[1]
    feature=sys.argv[2]
    dim=sys.argv[3]

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
    results = pd.read_csv(f"/scratch/tyoeasley/WAPIAW3/multiclass/output/{brainrep}_{feature}.csv", header=None)
    Y_all = results[0]
    y_pred = results[1]
    cm = confusion_matrix(Y_all, y_pred) 

    ############
    inspect_cm(cm, labels)
    save_figure(cm,labels,brainrep,feature)
