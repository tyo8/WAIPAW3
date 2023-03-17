#!/bin/bash

set -o nounset

# constants
base_dir="/scratch/tyoeasley/WAPIAW3"
pred_dir="${base_dir}/job_submission_portal/cross-prediction"
out_dir="${base_dir}/cross-prediction_outputs"
build_path_src="${base_dir}/utils/build_fpath_from_specs.sh"

# learning parameters
subjgrp_model_flist="${base_dir}/subject_lists/lists_of_groups/small_dummy_group.txt"
subjgrp_pred_flist="${base_dir}/subject_lists/lists_of_groups/small_dummy_group.txt"
spec_list_flist="${pred_dir}/spec_list_test.txt"
n_splits=100

# submission parameters
n_jobs=1
mem_gb=$(( 100/${n_jobs} ))
maxtime_str="23:55:00"

while getopts ":i:o:b:p:s:r:n:N:t:m:" opt; do
  case $opt in
    i) spec_list_fpath=${OPTARG}
    ;;
    o) out_dir=${OPTARG}
    ;;
    b) base_dir=${OPTARG}
    ;;
    p) pred_dir=${OPTARG}
    ;;
    s) subjgrp_model_flist=${OPTARG}
    ;;
    r) subjgrp_pred_flist=${OPTARG}
    ;;
    n) n_jobs=${OPTARG}
    ;;
    N) n_splits=${OPTARG}
    ;;
    t) maxtime_str=${OPTARG}
    ;;
    m) mem_gb=${OPTARG}
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    exit 1
    ;;
  esac

  case $OPTARG in
    -*) echo "Option $opt needs a valid argument"
    exit 1
    ;;
  esac
done

subjgrp_model_list=$( cat ${subjgrp_model_flist} )
subjgrp_pred_list=$( cat ${subjgrp_pred_flist} )
spec_list=$( cat ${spec_list_fpath} )

########################## Write the input and the script #########################

echo "Running predictions for the following parameters:"
echo "brainrep and feature parameters specified in: ${spec_list_fpath}"
echo "Models pulled from subject groups: ${subjgrp_model_flist}"
echo "Models used to cross-predict subjects in group: ${subjgrp_pred_flist}"
echo ""

for spec_line in $spec_list
do
	brainrep=$( echo $spec_line | cut -d_ -f 1 )
	feature=${spec_line##"${brainrep}_"}
	for modsubj_group in ${subjgrp_model_list}
	do
		# extract name of (model) group from filepath
		model_groupname=$( basename ${modsubj_group} | cut -d. -f 1 )
		
		# combine group name, brainrep name, and feature name to specify model choice
		model_name="splitmods_${model_groupname}_${brainrep}_${feature}"

		# parlay model name into path of directory holding all split-learned models of relevant type
		model_dir="${base_dir}/classification_model/cross-classifier_models/${model_name}"
     
		echo "Predicting with models found in directory: ${model_dir}"
		echo "..."

		for predsubj_group in ${subjgrp_pred_list}
		do
			# extract name of (prediction) group from filepath
			predsubj_groupname=$( basename ${predsubj_group} | cut -d. -f 1 )

			# combine model and prediction group info to specify cross-prediction task (brainrep & feature are fixed)
			job_name="predict_${predsubj_groupname}_from_${model_name/splitmods_/}"

			# use 'job_name' (specified above) to give paths to the submission script location and logfile locations
			log_fpath="${pred_dir}/cross-prediction_scripts/logs/${job_name}"
			sbatch_fpath="${pred_dir}/cross-prediction_scripts/do_${job_name}"
			echo "Cross-prediction submission script filepath:  ${sbatch_fpath}"

			# build path to load-in data given (prediction) group name, brainrep, and feature
			# (from script specified in variable 'build_path_src')
			datapath_type=$( ${build_path_src} ${predsubj_groupname} ${brainrep}  ${feature} )
			if compgen -G ${sbatch_fpath} >> "/dev/null"
			then
				rm $sbatch_fpath
			fi
			if compgen -G "${log_fpath}."* >> "/dev/null"
			then
				rm -f ${log_fpath}.*
			fi
			echo "Predicting diagnosis from ${brainrep} ${feature} in subject group: ${predsubj_groupname}"	
			echo "\
\
#!/bin/sh
#SBATCH --job-name=${job_name}
#SBATCH --output=${log_fpath}.out%j
#SBATCH --error=${log_fpath}.err%j
#SBATCH --time=${maxtime_str}
#SBATCH --partition=small
#SBATCH --cpus-per-task=${n_jobs}
#SBATCH --mem-per-cpu=${mem_gb}gb

# constants
classifier=\"${base_dir}/classification_model/cross-classify_patients.py\"
patient_eid_dir=\"${base_dir}/subject_lists/patient_eid\"

# input parameters
subj_list=\"${predsubj_group}\"
datapath_type=\"${datapath_type}\"
model_fpath_type=\"${model_dir}/split_%s.pkl\"
pred_outpath=\"${out_dir}/${job_name/predict/metrics}.csv\"

# resource & computation parameters
n_jobs=${n_jobs}                # number of cores requested by process
rng_seed=0              # random seed state integer

# (bagged) classifier parameters
folds=5                 # number of folds during gridsearch hyperparameter validation
n_splits=${n_splits}            # number of random train/validation splits within training data=number of models learned
n_estimators=250        # number of trees in random forest

python \${classifier} -l \${subj_list} -f \${datapath_type} -r \${pred_outpath} -m \${model_fpath_type} -p \${patient_eid_dir} \\
        -n \${n_jobs} -R \${rng_seed} \\
        -k \${folds} -s \${n_splits} -e \${n_estimators} -v
\
" > "${sbatch_fpath}"  

			# Overwrite submission script# Make script executable
			chmod 770 "${sbatch_fpath}" || { echo "Error changing the script permission!"; exit 1; }

			# Submit script
			sbatch "${sbatch_fpath}" || { echo "Error submitting jobs!"; exit 1; }
		done
	done
done
