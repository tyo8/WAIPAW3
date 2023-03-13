#!/bin/bash

set -o nounset

# bookkeeping parameters
base_dir="/scratch/tyoeasley/WAPIAW3"
diffusion_gradient_dir="${base_dir}/brainrep_data/diffusion_gradient_data"
script_dir="${base_dir}/job_submission_portal/extraction/brainrep_xtr_scripts"

# data option parameters
subj_group_fpath="${base_dir}/subject_lists/all_subj_eid.csv"

# parcellation parameters
dim=40

# computational parameters
mem_gb=250
maxtime_str="23:55:00"

while getopts ":b:S:s:d:n:r:m:t:" opt; do
  case $opt in
    b) base_dir=${OPTARG}
    ;;
    S) diffusion_gradient_dir=${OPTARG}
    ;;
    s) subj_group_fpath=${OPTARG}
    ;;
    d) dim=${OPTARG}
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
        echo "extracting ${dim}-dimensional diffusion gradeints for sub-${subj_ID}..."

        job_name="diffgrad_subj-${subj_ID}"

        sbatch_fpath="${script_dir}/do_${job_name}"
        log_fpath="${script_dir}/logs/${job_name}"

        if compgen -G ${sbatch_fpath}
        then
                rm $sbatch_fpath
        fi
        echo "\
\
#!/bin/sh
#SBATCH --job-name=${job_name}
#SBATCH --output=\"${log_fpath}.out\"
#SBATCH --error=\"${log_fpath}.err\"
#SBATCH --time=${maxtime_str}
#SBATCH --mem=${mem_gb}GB

# constants
grad_scr=\"/scratch/tyoeasley/WAPIAW3/brainrep_data/diffusion_gradient_data/processing/compute_subj_gradients.py\"
mask_path=\"/scratch/tyoeasley/WAPIAW3/brainrep_data/final_GM_mask.nii.gz\"

# inputs
outpath_type=\"/scratch/tyoeasley/WAPIAW3/brainrep_data/diffusion_gradient_data/subj_gradients/sub-%s.csv\"
dim=${dim}
sID=\"${subj_ID}\"

source /export/anaconda/anaconda3/anaconda3-2020.07/bin/activate neuro
python \${grad_scr} \${sID} -n \${dim} -o \${outpath_type} -m \${mask_path} --par
\
" > "${sbatch_fpath}"

        # Overwrite submission script# Make script executable
        chmod 771 "${sbatch_fpath}" || { echo "Error changing the script permission!"; exit 1; }

        # Submit script
        sbatch "${sbatch_fpath}" || { echo "Error submitting jobs!"; exit 1; }
done
