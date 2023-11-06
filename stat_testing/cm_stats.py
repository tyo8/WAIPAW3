import sys
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress 
from sklearn.metrics import confusion_matrix

# statistical summary of confusion matrix entries and properties
def inspect_cm(cm, labels):
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
        "Proportion of sample in class": rowsum/sum(rowsum),
        "Proportion of predictions in class": colsum/(sum(colsum))
        }, index=labels)
    print("Precision summary of confusion matrix:")
    print(stats_summary)

    stats_summary.drop(
            # columns=["Sensitivity", "Specificity", "#true_pos", "#false_pos", "#true_neg", "#false_neg"], 
            index="Other disorders",
            inplace=True)
    x = rowsum[colsum > 0]
    y = colsum[colsum > 0]
    result = linregress(x, np.log10(y))
    print(f"Association strength of class size and log(prediction Proportion): R^2 = {result.rvalue**2}. Further details below.")
    print(result)

    fig, ax = plt.subplots()
    stats_summary.plot( "Proportion of sample in class", "Proportion of predictions in class", kind="scatter", ax=ax)
    ax.set_yscale("log")
    plt.title("Classification likelihood as a function of class size")
#    for i, data in stats_summary.iterrows():
#        if "Demy" in i or "Health" in i:
#            plt.annotate(i, data, ha='left', rotation=0)
    plt.savefig("sampsize_vs_classification.png",dpi=600)

#####################################################################################

    x = rowsum/sum(rowsum)
    y = TPR
    from scipy.optimize import curve_fit
    opt_pars, cov_pars = curve_fit(_exp_fit,x,y)
    print(f"Fit {len(opt_pars)} parameters to model from x-data of shape {x.shape} and y-data of shape {y.shape}")
    ypred = _exp_fit(x, *opt_pars)
    R2,result = _pseudo_R2(ypred, y, r2type="exp")
    print(f"Association strength of class size and sensitivity: R^2 = {R2}. Only pseudo. Exponential fit params:")
    print(opt_pars)
    if result:
        print(result)

    x_sm = np.linspace(min(x), max(x), 250)
    y_sm = _exp_fit(x_sm, *opt_pars)

    fig, ax = plt.subplots()
    # stats_summary.plot( "Proportion of sample in class" , "Sensitivity", kind="scatter", ax=ax)
    plt.scatter( rowsum/sum(rowsum), TPR)
    plt.plot(x_sm, y_sm, 'r-')
    ax.set_xlabel( "Proportion of sample in class" )
    ax.set_ylabel( "Sensitivity (true positive rate)" )
    plt.title("True positive rate as a function of class size")
    for i, data in enumerate(TPR):
        if "Demyel" in labels[i]:
            plt.annotate("  "+labels[i], [x[i], data], ha='left', rotation=30)
    plt.savefig("sampsize_vs_TPR.png",dpi=600)


def _exp_fit(x, a, b, c):
    return a * np.exp(b * x) + c

# calculates a "pseudo-R^2" for nonlinear fits; no longer as valid as in linear case, perhaps still instructive.
def _pseudo_R2(ypred, y, r2type="gen"):
    if r2type=="exp":
        # calculates "R2" for *expected* exponential model; i.e., log y ~ linear
        Y = [ obs for i,obs in enumerate(y) if obs > 0 and ypred[i] > 0]
        Ypred = [ obs for i,obs in enumerate(ypred) if obs > 0 and y[i] > 0]
        res_ypred = sum(np.power(np.log(Ypred) - np.log(Y), 2))
        var_y = sum(np.power(np.log(Ypred) - np.log(np.mean(y)), 2))
        pseudo_R2 = 1 - res_ypred/var_y
        result = []

    elif r2type=="gen":
        res_ypred = sum(np.power(ypred - y, 2))
        var_y = sum(np.power(y - np.mean(y), 2))
        pseudo_R2 = 1 - res_ypred/var_y
        result = []

    elif r2type=="lin":
        result = linregress(ypred, y)
        pseudo_R2 = result.rvalue**2

    return pseudo_R2, result


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
