#!/bin/bash

set -o nounset

# bookkeeping parameters
base_dir="/scratch/tyoeasley/WAPIAW3"
PROFUMO_dir="${base_dir}/brainrep_data/PROFUMO_data"

# run & data option parameters
dim=25
subj_group_flist="${base_dir}/subject_lists/lists_of_groups/code_disease_groups.txt"

while getopts ":b:P:s" opt; do
  case $opt in
    b) base_dir=${OPTARG}
    ;;
    P) PROFUMO_dir=${OPTARG}
    ;;
    s) subj_group_flist=${OPTARG}
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

job_name="PFM"

for subj_group in ${subj_group_list}
do
	echo ""
        echo "submitting ${dim}-dimensional PFM in subject group: ${subj_group}"
\
#!/bin/sh

#SBATCH --job-name=${job_name}_d${dim}
#SBATCH --output=${PROFUMO_dir}/logs/${job_name}_d${dim}.out
#SBATCH --error=${PROFUMO_dir}/logs/${job_name}_d${dim}.err
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --mem=100G

# constants
base_dir=\"\/scratch/tyoeasley/WAPIAW3\"
mk_json=\"${PROFUMO_dir}/create_datalocation.sh\"

# user specifications
subj_list=${subj_group}
groupname=$( basename ${subj_list} | cut -d. -f 1 )
src_json_type="$( echo \"/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/raw_data_subj_lists/${groupname}_datalocations.json\" )"

# derivatives
src_json=$( ${mk_json} -b ${base_dir} -s ${subj_list} -j ${src_json_type} )

#lines to run PFM
module load singularity/3.5.2

container=/home/e.ty/profumo.sif
dim=25
mask_fpath=\"${base_dir}/brainrep_data/final_GM_mask.nii.gz\"
scr_json=\"${PROFUMO_dir}/raw_data_subj_lists/${groupname}_datalocations.json\"
output=/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/out_PROFUMO/${groupname}_${dim}.pfm

singularity exec -B /scratch:/scratch -B /ceph:/ceph ${container}  /opt/profumo/C++/PROFUMO ${src_json} ${dim} ${output} --useHRF 0.735 --hrfFile /opt/profumo/HRFs/Default.phrf --mask ${mask_fpath} --covModel Subject --dofCorrection 0.075

done
