#!/bin/bash

set -o nounset

# bookkeeping parameters
base_dir="/scratch/tyoeasley/WAPIAW3"
xtr_dir="${base_dir}/brainrep_data/ICA_data/extract_feats"
xtr_script="${xtr_dir}/feats_from_dtseries.py"

# data parameters
dimlist_fpath="${base_dir}/brainrep_data/ICA_data/ICA_dimlist.txt"
subj_group_flist="${base_dir}/subject_lists/lists_of_groups/test_groups.txt"
input_gendir=$( printf "/scratch/tyoeasley/WAPIAW3/brainrep_data/ICA_data/dual_regression/%s/ica%s/groupICA%s.dr" \${groupname} \${dim} \${dim} )


# submission parameters
sbatch_fpath="${xtr_dir}/do_extract_ICA_feats"
job_name="featxtr_ICA"
maxtime_str="23:55:00"

while getopts ":b:d:x:f:D:s:i:n:t:" opt; do
  case $opt in
    b) base_dir=${OPTARG}
    ;;
    d) xtr_dir=${OPTARG}
    ;;
    x) xtr_script=${OPTARG}
    ;;
    D) dimlist_fpath=${OPTARG}
    ;;
    s) subj_group_flist=${OPTARG}
    ;;
    i) input_gendir=${OPTARG}
    ;;
    f) sbatch_fpath=${OPTARG}
    ;;
    n) job_name=${OPTARG}
    ;;
    t) maxtime_str=${OPTARG}
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

subj_group_list=$( cat ${subj_group_flist} )

########################## Write the input and the script #########################

echo "general input path is of the form: ${input_gendir}"

for dim in $(cat ${dimlist_fpath})
do
	for subj_group in ${subj_group_list}
	do
		groupname=$( basename ${subj_group} | cut -d. -f 1 )
		input_dir=${input_gendir}
		echo ""
		echo "extracting features from ${dim}-dimensional data subject group: ${groupname}"	
		echo "\
\
#!/bin/sh

#SBATCH --job-name=${job_name}
#SBATCH --account=janine_bijsterbosch
#SBATCH --output=${xtr_dir}/logs/${job_name}_${dim}_${groupname}.out
#SBATCH --error=${xtr_dir}/logs/${job_name}_${dim}_${groupname}.err
#SBATCH --time=${maxtime_str}
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --mem=50GB

# constants
xtr_script=\"${xtr_script}\"

# user specs
group=\"${subj_group}\"
groupname=\"${groupname}\"
dim=${dim}

# derivatives
input_dir=\"${input_dir}\"

python \${xtr_script} -i \${input_dir} -d \${dim} -g \${group}

\
" > "${sbatch_fpath}"  

		# Overwrite submission script# Make script executable
		chmod 771 "${sbatch_fpath}" || { echo "Error changing the script permission!"; exit 1; }

    		# Submit script
    		sbatch "${sbatch_fpath}" || { echo "Error submitting jobs!"; exit 1; }
	done
done

