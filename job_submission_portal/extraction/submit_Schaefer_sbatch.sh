#!/bin/bash

set -o nounset

# bookkeeping parameters
base_dir="/scratch/tyoeasley/WAPIAW3"
Schaefer_dir="${base_dir}/brainrep_data/Schaefer_data"
script_dir="${base_dir}/job_submission_portal/extraction/brainrep_xtr_scripts"

# data option parameters
subj_group_fpath="${base_dir}/subject_lists/all_subj_eid.csv"
overwrite=false

# parcellation parameters
dim=400
networks=17
res=2

# computational parameters
mem_gb=150
maxtime_str="23:55:00"

while getopts ":b:S:s:w:d:n:r:m:t:" opt; do
  case $opt in
    b) base_dir=${OPTARG}
    ;;
    S) Schaefer_dir=${OPTARG}
    ;;
    s) subj_group_fpath=${OPTARG}
    ;;
    w) overwrite=${OPTARG}
    ;;
    d) dim=${OPTARG}
    ;;
    n) networks=${OPTARG}
    ;;
    r) res=${OPTARG}
    ;;
    m) mem_gb=${OPTARG}
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

subj_ID_list=$( cat ${subj_group_fpath} )

########################## Write the input and the script #########################


for subj_ID in ${subj_ID_list}
do
        echo "extracting ${dim}-dimensional Schaeffer parcellation (${networks} networks, res=${res}mm) for sub-${subj_ID}..."

        job_name="ts_schaefer_d${dim}_n${networks}_${res}mm"

        sbatch_fpath="${script_dir}/do_${job_name}"
        log_fpath="${script_dir}/logs/${job_name}"

        if compgen -G ${sbatch_fpath}
        then
                rm $sbatch_fpath
        fi
        if compgen -G "${log_fpath}.out"*
        then
                rm -f ${log_fpath}.*
        fi
        echo "\
\
#!/bin/sh
#SBATCH --job-name=${job_name}
#SBATCH --output=${Schaefer_dir}/logs/${job_name}_${subj_ID}.out
#SBATCH --error=${Schaefer_dir}/logs/${job_name}_${subj_ID}.err
#SBATCH --time=${maxtime_str}
#SBATCH --mem=${mem_gb}GB

ext_scr=\"/scratch/tyoeasley/WAPIAW3/brainrep_data/Schaefer_data/pull_schaefer_timeseries.py\"

dim=${dim}
networks=${networks}
res=${res}

subj_ID=\"${subj_ID}\"

source /export/anaconda/anaconda3/anaconda3-2020.07/bin/activate neuro
\
" > "${sbatch_fpath}"

	if ( $overwrite )
	then 
		echo "\
python \${ext_scr} -s \${subj_ID} -D \${dim} -n \${networks} -r \${res} -w
		" >> "${sbatch_fpath}"
	else
		echo "\
python \${ext_scr} -s \${subj_ID} -D \${dim} -n \${networks} -r \${res}
		" >> "${sbatch_fpath}"
	fi



        # Overwrite submission script# Make script executable
        chmod 771 "${sbatch_fpath}" || { echo "Error changing the script permission!"; exit 1; }

        # Submit script
        sbatch "${sbatch_fpath}" || { echo "Error submitting jobs!"; exit 1; }
done
