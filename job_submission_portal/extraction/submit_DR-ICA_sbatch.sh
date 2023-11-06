#!/bin/bash

set -o nounset

# bookkeeping parameters
base_dir="/scratch/tyoeasley/WAPIAW3"
ICA_dir="${base_dir}/brainrep_data/ICA_data"
script_dir="${base_dir}/job_submission_portal/extraction/brainrep_xtr_scripts"
maxtime_str="24:55:00"
partition="tier2_cpu"

# run & data option parameters
dim_list_fpath="${ICA_dir}/ICA_dimlist.txt"
subj_group_flist="${base_dir}/subject_lists/lists_of_groups/code_disease_groups.txt"
DR_process_script="up_to_stage1_DR_slurm"
	### options:
	# mask_only_slurm
	# stage1_DR_only_slurm
	# up_to_stage1_DR_slurm


while getopts ":b:I:t:f:D:s:p:P:" opt; do
  case $opt in
    b) base_dir=${OPTARG}
    ;;
    I) ICA_dir=${OPTARG}
    ;;
    t) maxtime_str=${OPTARG}
    ;;
    D) dim_list_fpath=${OPTARG}
    ;;
    s) subj_group_flist=${OPTARG}
    ;;
    p) DR_process_script=${OPTARG}
    ;;
    P) partition=${OPTARG}
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


for dim in $(cat ${dim_list_fpath})
do
	for subj_group in ${subj_group_list}
	do
		groupname=$( basename ${subj_group} | cut -d. -f 1)
		process_name=$(echo $DR_process_script | cut -d_ -f 1)

		job_name="dr-ica_${process_name}_${groupname}_d${dim}"
		sbatch_fpath="${script_dir}/do_dr-ica${dim}_${groupname}"
		log_fpath="${script_dir}/logs/${job_name}"

		echo ""
		echo "submitting ${dim}-dimensional DR-ICA computation in subject group: ${subj_group}"	
		if compgen -G ${sbatch_fpath} >> "/dev/null"
		then
			rm $sbatch_fpath
		fi
		if compgen -G "${log_fpath}."* >> "/dev/null"
		then
			rm -f ${log_fpath}.*
		fi
		echo "\
\
#!/bin/sh -l

#SBATCH --exclude=node03
#SBATCH --job-name=\"${job_name}\"
#SBATCH --account=janine_bijsterbosch
#SBATCH --output=\"${log_fpath}.out%j\"
#SBATCH --error=\"${log_fpath}.err%j\"
#SBATCH --time=${maxtime_str}
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --partition=${partition}
#SBATCH --mem=50gb

# constants
base_dir=\"/scratch/tyoeasley/WAPIAW3\"
mask_fpath=\"\${base_dir}/brainrep_data/final_GM_mask.nii.gz\" 
mk_descon=\"\${base_dir}/brainrep_data/ICA_data/rand_design_con.py\"
mk_flist=\"\${base_dir}/utils/eid_to_fpath.sh\"
fpath_pattern=\"/ceph/biobank/derivatives/melodic/sub-%s/ses-01/sub-%s_ses-01_melodic.ica/filtered_func_data_clean_MNI152.nii.gz\"

# user specifications
dim=${dim}
eid_list=\"${subj_group}\"

# derivatives
groupname=${groupname}
melodic_out=\"\${base_dir}/brainrep_data/ICA_data/melodic_output/\${groupname}/ica\${dim}\"
DR_out=\${melodic_out/\"melodic_output\"/\"dual_regression\"}
design_fpath_type=\"\${DR_out}/design\"
data_flist=\"\${base_dir}/brainrep_data/ICA_data/raw_data_subj_lists/\${groupname}.txt\"

if ! test -f \"\${data_flist}\"
then
	\${mk_flist} -i \${eid_list} -o \${data_flist} -p \${fpath_pattern}
fi

n_subj=\$(cat \${data_flist} | wc -l )

# output
echo \"pulling from subject list: \${eid_list}\"
echo \"pulling subject data from generalized filepath: \${fpath_pattern}\"
echo \"        (list of filenames of preprocessed data can be found in): \${data_flist}\"
echo \"computing \${dim} independent components\"
echo \"sending melodic outputs to: \${melodic_out}\"
if ! test -d \${melodic_out}
then
	mkdir -p \${melodic_out}
fi
echo \"sending dual_regression outputs to: \${DR_out}\"
if ! test -d \${DR_out}/groupICA\${dim}.dr
then
	mkdir -p \${DR_out}/groupICA\${dim}.dr
fi

# create (mock) design matrices
module load python
python \${mk_descon} -n \${n_subj} --fpath_noext \${design_fpath_type}

# load FSL module
module load fsl
export DISPLAY=:1

if ! compgen -G \"\${melodic_out}/melodic_IC.nii.gz\" >> "/dev/null"
then
	echo \"\"
	echo \"(re?-)computing melodic data for \${groupname}...\"
	echo \"Start: \$(date)\"
	melodic -i \${data_flist} -o \${melodic_out} --tr=0.72 --nobet -a concat -m \${mask_fpath} --report --Oall -d \${dim}
	echo \"Finish: \$(date)\"
	echo \"\"
fi

/scratch/tyoeasley/WAPIAW3/brainrep_data/ICA_data/FSL_slurm/${DR_process_script} \"\${melodic_out}/melodic_IC.nii.gz\" \${dim} \"\${design_fpath_type}.mat\" \"\${design_fpath_type}.con\" 0 \"\${DR_out}/groupICA\${dim}.dr\" \$(cat \${data_flist})

chmod -R 771 \${DR_out}
\
" > "${sbatch_fpath}"  # Overwrite submission script

		# Make script executable
		chmod 771 "${sbatch_fpath}" || { echo "Error changing the script permission!"; exit 1; }

    		# Submit script
    		sbatch "${sbatch_fpath}" || { echo "Error submitting jobs!"; exit 1; }
	done
done

