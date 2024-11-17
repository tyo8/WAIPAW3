# Opaque Ontology: Neuroimaging Classification of ICD-10 Diagnostic Groups in the UK Biobank
Source and cluster submission code for transdiagnostic patient-control classification in 17 ICD-10 diagnostic groups in the UK BioBank dataset.

## Rough Overview
This repository contains code for and records the directory tree structure of the project published (in GigaScience; [bioarXiv preprint](https://doi.org/10.1101/2024.04.15.589555)) as
- T. Easley, X. Luo, K. Hannon, P. Lenzini, and J. Bijsterbosch, “Opaque Ontology: Neuroimaging Classification of ICD-10 Diagnostic Groups in the UK Biobank,” bioRxiv, p. 2024.04.15.589555, Apr. 2024, doi: 10.1101/2024.04.15.589555. 

The diretories of this repository are roughly subdivided into three categories of function:
1. data selection and pre-processing
2. specification and deployment of classification models
4. visualization and post-hoc statistical analysis of classification results

## Structure of the repository

The directory-wise contents of each function category are a given detailed overview below.

### Data Selection and Pre-processing Pipeline
The data generation pipeline splits into two main components: developing patient/control lists based on inclusion/matching criteria and generating neuroimaging features.

#### brainrep_data
Note that no subject data of any kind is included in this public repository! Instead, the following directories contain the extraction/computation/processing code used to create differentiate types of feature sets within each ICD-10 diagnostic group. Wherever relevant, group-level analyses were computed anew for each group. 
- <ins>gradient_data</ins>: code to compute diffusion-network based [gradient representations](https://pubmed.ncbi.nlm.nih.gov/27791099/) from connectivity data at both the subject and group level 
- <ins>ICA_data</ins>: sub-repository to execute ICA dual-regression (ICA-DR) procedure within each diagnostic group -- [melodic](https://fsl.fmrib.ox.ac.uk/fslcourse/graduate/lectures/practicals/ica/) group regression and [ICA dual regression](https://open.win.ox.ac.uk/pages/fslcourse/practicals/ica/index.html), both implemented in [FSL](https://fsl.fmrib.ox.ac.uk/fsl/docs/#/), and addtional code for extracting secondary features (FC network matrices, partial FC matrices, and amplitudes)
- <ins>PROFUMO_data</ins>: sub-repository for the computation of the [PROFUMO](https://git.fmrib.ox.ac.uk/samh/profumo) parcellation for each diagnostic group, and additional code for extracting secondary features (FC network matrices, spatial correlation matrices, and amplitudes)
- <ins>Schaefer_data</ins>: code for extracting parcellation-level timeseries from data and computing FC network matrices, partial FC matrices, and amplitude features from [Schaefer-parcellated](https://academic.oup.com/cercor/article/28/9/3095/3978804) data
- <ins>T1_data</ins>: storage location for [Freesurfer](https://surfer.nmr.mgh.harvard.edu/)-extracted structural volume and cortical surface features from T1-weighted structural MRI scans
- <ins>sociodemographic</ins>: cotains data cleaning and feature extraction code to pull sociodemographic features from the UKB biobank for all subjects.

#### subject_lists
Repository containing lists of electronic ID numbers (eIDs) of patients in each diagnostic group, code for selecting corresponding matched healthy controls, and matched patient/control lists. Also contains some code and eID lists used to troubleshoot problems encountered in the UKB with incomplete or corrupted imaging, diagnostic, or sociodemographic data.

### Subject Classification Pipeline
Subject classification code specifies, parameterizes, and propogates the classification model. This pipeline assumes that classification is deployed massively in parallel on a distributed system (e.g., high-performance computing cluster) operating under a SLURM queue manager.

#### classification_model
This directory contains the two most important pieces of code in the repository: `classify_patients.py` and `model_specification.py`. These python mini-modules are the central workhorse of the classification project.

#### multiclass
Adapts the binary prediction engine to a multiclass setting in `multiclass.py`.

#### job_submission_portal
Central hub for infrastructural bash scripts to assign, distribute, and organize the submission of compute jobs to the job manager. Split into three classes of jobs:
- <ins>cross-prediction</ins>: multiclassification jobs
- <ins>extraction</ins>: jobs extracting neuorimaging predictive features from raw scan data
- <ins>prediction</ins>: jobs classifying patients vs. controls within diagnostic groups

#### utils
General-purpose bash code to perform basic bookkeeping functions while navigating large collections of UK BioBank data on the compute cluster.

### Statistical Testing and Visualization Pipeline
Both the `figure` (results visualization) and `stat_testing` (post-hoc statistical analysis of results) directories contain code referencing directories not present in this repository (i.e., `prediction_outputs` and `cross-prediction outs`), whose outputs would need to be created to test the replicability of our findings.

#### figures
Visualization code producing summary swarm plots of prediction outputs under varying experimental conditions.

#### stat_testing
Code to compute statsitcal signficance testing with family-wise error correction and statistical summarization of the multiclass prediction's confusion matrix.

## Preparing the Computing Environment
As much as possible, we confined our architecture to commonly used and publicly available code and packages. However, because of the large-scale nature of the problem at hand, our code reflects our use of a high-performance computing cluster (managed, in our case, with SLURM).

### Software Dependecies
The analyses in this have several dependencies; they are listed below according to their functional role.

<ins>Neuroimaging Data Pre-processing</ins>:
- [nibabel](https://nipy.org/nibabel/)
- [FSL](https://fsl.fmrib.ox.ac.uk/fsl/docs/#/)
- [PROFUMO](https://git.fmrib.ox.ac.uk/samh/profumo)
	
<ins>Classification and Processing</ins>:
- [numpy](https://numpy.org/)
- [scipy](https://scipy.org/)
- [pandas](https://pandas.pydata.org/)
- [scikit-learn](https://scikit-learn.org/stable/)

<ins>Figures</ins>:
- [seaborn](https://seaborn.pydata.org/)
- [matplotlib](https://matplotlib.org/stable/index.html)
	

### Queue Management and Cluster Computing
As stated elsewhere above, the pipelines in this repository were designed for use on a high-performance cluster with SLURM job management.

## Academic use

This code is available and is fully adaptable for individual user customization. If you use the our methods, please cite as the following:

T. Easley, X. Luo, K. Hannon, P. Lenzini, and J. Bijsterbosch, “Opaque Ontology: Neuroimaging Classification of ICD-10 Diagnostic Groups in the UK Biobank,” bioRxiv, p. 2024.04.15.589555, Apr. 2024, doi: 10.1101/2024.04.15.589555. 
