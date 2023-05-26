#!/bin/bash

set -o nounset

# bookkeeping parameters
base_dir="/scratch/tyoeasley/WAPIAW3"
PROFUMO_dir="${base_dir}/brainrep_data/PROFUMO_data"
script_dir="${base_dir}/job_submission_portal/extraction/brainrep_xtr_scripts"

# data option parameters
dimlist_fpath="${PROFUMO_dir}/dimlist.txt"
subj_group_flist="${base_dir}/subject_lists/lists_of_groups/test_groups.txt"

# computational parameters
maxtime_str="167:55:00"

while getopts ":b:P:s:d:t:" opt; do
  case $opt in
    b) base_dir=${OPTARG}
    ;;
    P) PROFUMO_dir=${OPTARG}
    ;;
    s) subj_group_flist=${OPTARG}
    ;;
    d) dimlist_fpath=${OPTARG}
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
dimlist=$( cat ${dimlist_fpath} )

########################## Write the input and the script #########################


for dim in ${dimlist}
do
	for subj_group in ${subj_group_list}
	do
		echo ""
		echo "submitting ${dim}-dimensional PFM in subject group: ${subj_group}"

		n_subj=$( cat ${subj_group} | wc -l )
		mem_gb=$(( 32*${n_subj}/100 + 10 ))

		groupname=$( basename ${subj_group} | cut -d. -f 1 )
		sbatch_fpath="${script_dir}/do_PROFUMO_d${dim}_${groupname}"
                job_name="PFMd${dim}_${groupname}"
		log_fpath="${script_dir}/logs/${job_name}"

		if compgen -G ${sbatch_fpath} >> "/dev/null"
		then
			rm $sbatch_fpath
		fi
                if compgen -G "${log_fpath}.out" >> "/dev/null"
                then
                        rm -f ${log_fpath}.*
                fi
		echo "batch script saving to path ${sbatch_fpath}"
		echo "\
\
#!/bin/sh

#SBATCH --job-name=${job_name}
#SBATCH --output=${log_fpath}.out
#SBATCH --error=${log_fpath}.err
#SBATCH --time=${maxtime_str}
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --mem=${mem_gb}GB

# constants
base_dir=\"/scratch/tyoeasley/WAPIAW3\"
mk_json=\"${PROFUMO_dir}/create_datalocation.sh\"

# user specifications
subj_list=\"${subj_group}\"
groupname=\"${groupname}\"
src_json_fpath=\"/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/raw_data_subj_lists/${groupname}_datalocations.json\"

# derivatives
\${mk_json} -b \${base_dir} -s \${subj_list} -j \${src_json_fpath}

#lines to run PFM
module load singularity/3.5.2

container=\"/home/e.ty/profumo.sif\"
dim=${dim}
mask_fpath=\"\${base_dir}/brainrep_data/final_GM_mask.nii.gz\"
scr_json=\"\${PROFUMO_dir}/raw_data_subj_lists/\${groupname}_datalocations.json\"
output=\"/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/out_PROFUMO/\${groupname}_\${dim}.pfm\"

singularity exec -B /scratch:/scratch -B /ceph:/ceph \${container}  /opt/profumo/C++/PROFUMO \${src_json_fpath} \${dim} \${output} --useHRF 0.735 --hrfFile /opt/profumo/HRFs/Default.phrf --mask \${mask_fpath} --covModel Subject --dofCorrection 0.075
\
" > "${sbatch_fpath}"

                # Overwrite submission script# Make script executable
                chmod 771 "${sbatch_fpath}" || { echo "Error changing the script permission!"; exit 1; }

                # Submit script
                sbatch "${sbatch_fpath}" || { echo "Error submitting jobs!"; exit 1; }
	done
done
