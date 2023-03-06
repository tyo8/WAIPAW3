#!/bin/bash

set -o nounset

# bookkeeping parameters
base_dir="/scratch/tyoeasley/WAPIAW3"
PROFUMO_dir="${base_dir}/brainrep_data/PROFUMO_data"
sbatch_fpath="${PROFUMO_dir}/do_dual_reg_batch"

# run & data option parameters
subj_group_flist="${base_dir}/subject_lists/lists_of_groups/code_disease_groups.txt"


while getopts ":b:I:f:D:s:p:" opt; do
  case $opt in
    b) base_dir=${OPTARG}
    ;;
    I) PROFUMO_dir=${OPTARG}
    ;;
    f) sbatch_fpath=${OPTARG}
    ;;
    D) dim_list_fpath=${OPTARG}
    ;;
    s) subj_group_flist=${OPTARG}
    ;;
    p) DR_process_script=${OPTARG}
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

job_name="DR_pipeline"

for dim in $(cat ${dim_list_fpath})
do
	for subj_group in ${subj_group_list}
	do
		echo ""
		echo "submitting ${dim}-dimensional DR-PROFUMO computation in subject group: ${subj_group}"	
		echo "\
\
#!/bin/sh
#SBATCH -J pfm
#SBATCH -o logs/pfm_out.o%j
#SBATCH -e logs/pfm_err.e%j
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mem 100G
#SBATCH -t 5:00:00

# constants
base_dir="/scratch/tyoeasley/WAPIAW3"
mk_json="/scratch/tyoeasely/WAPIAW3/brainrep_data/PROFUMO_data/create_datalocations.sh"

# input parameters
subj_list=${subj_group}
src_json_type=\"\$( echo \"/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/raw_data_subj_lists/\${groupname}_datalocations.json\" )\"

# derivatives
groupname=\$( basename \$subj_list | cut -d. -f 1 )
src_json=\$( \${mk_json} -b \${base_dir} -s \${subj_list} -j \${src_json_type} )

# PROFUMO parameters
module load singularity/3.5.2
container=/home/e.ty/profumo.sif
dim=25
mask=/scratch/tyoeasley/WAPIAW3/brainrep_data/final_GM_mask.nii.gz
output=/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/out_PROFUMO/${groupname}_${dim}.pfm

singularity exec -B /scratch/tyoeasley/WAPIAW3 -B /ceph:/ceph ${container}  /opt/profumo/C++/PROFUMO ${src_json} ${dim} ${output} --useHRF 0.735 --hrfFile /opt/profumo/HRFs/Default.phrf --mask ${mask} --covModel Subject --dofCorrection 0.075
\
" > "${sbatch_fpath}"  

		# Overwrite submission script# Make script executable
		chmod +x "${sbatch_fpath}" || { echo "Error changing the script permission!"; exit 1; }

    		# Submit script
    		sbatch "${sbatch_fpath}" || { echo "Error submitting jobs!"; exit 1; }
	done
	# echo "Waiting between dimension calls to avoid *stepping on toes*..."
	# sleep 90
	# echo "Done."
done

