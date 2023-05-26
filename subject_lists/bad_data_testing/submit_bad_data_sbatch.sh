#!/bin/bash

set -o nounset
sbatch_fpath="/scratch/tyoeasley/WAPIAW3/subject_lists/bad_data_testing/do_load_bad_data"

subj_fpath=""
subj_ID="<unknown>"

while getopts ":f:s:" opt; do
  case $opt in
    f) subj_fpath=${OPTARG}
    ;;
    s) subj_ID=${OPTARG}
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

########################## Write the input and the script #########################

echo "\
\
#!/bin/sh
#SBATCH --job-name=load_data
#SBATCH --output="/scratch/tyoeasley/WAPIAW3/subject_lists/bad_data_testing/logs/load_bad_data_${subj_ID}.out"
#SBATCH --error="/scratch/tyoeasley/WAPIAW3/subject_lists/bad_data_testing/logs/load_bad_data_${subj_ID}.err"
#SBATCH --time=23:55:00
#SBATCH --mem=10GB

pyscr="/scratch/tyoeasley/WAPIAW3/subject_lists/bad_data_testing/pull_neurodata.py"

subj_fpath=${subj_fpath}

source /export/anaconda/anaconda3/anaconda3-2020.07/bin/activate neuro
python \${pyscr} \${subj_fpath} || { echo \"${subj_ID}\" >> corrupted_data.txt; exit 1; }
\
" > "${sbatch_fpath}"

# Overwrite submission script# Make script executable
chmod 771 "${sbatch_fpath}" || { echo "Error changing the script permission!"; exit 1; }

# Submit script
sbatch "${sbatch_fpath}" || { echo "Error submitting jobs!"; exit 1; }
