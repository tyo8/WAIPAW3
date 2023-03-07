#!/bin/sh
#SBATCH -J call_PFM
#SBATCH -o logs/call_PFM.out%j
#SBATCH -e logs/call_PFM.err%j
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mem 100G
#SBATCH -t 23:55:00

# constants
base_dir="/scratch/tyoeasley/WAPIAW3"
PROFUMO_dir="${base_dir}/brainrep_data/PROFUMO_data"
script_fpath="${base_dir}/job_submission_portal/extraction/submit_PROFUMO_sbatch_edited.sh"

# parameters
subj_group_flist="${base_dir}/subject_lists/lists_of_groups/code_disease_groups.txt"

# call
${script_fpath} -b ${base_dir} -P ${PROFUMO_dir} -s ${subj_group_flist}
