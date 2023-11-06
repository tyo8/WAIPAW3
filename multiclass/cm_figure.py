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
