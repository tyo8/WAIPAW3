#!/bin/bash

set -o nounset

# bookkeeping parameters
base_dir="/scratch/tyoeasley/WAPIAW3"
ICA_dir="${base_dir}/brainrep_data/ICA_data"
sbatch_fpath="${ICA_dir}/do_dual_reg_batch"

# dataset parameters
dim_list_fpath="${ICA_dir}/ICA_dimlist.txt"
subj_group_flist="${base_dir}/subject_lists/lists_of_groups/code_disease_groups.txt"


while getopts ":b:I:f:d:s:" opt; do
  case $opt in
    b) base_dir=${OPTARG}
    ;;
    I) ICA_dir=${OPTARG}
    ;;
    f) sbatch_fpath=${OPTARG}
    ;;
    d) dim_list_fpath=${OPTARG}
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

for dim in $(cat ${dim_list_fpath})
do
	for subj_group in ${subj_group_list}
	do
		echo ""
		echo "submitting ${dim}-dimensional DR-ICA computation in subject group: ${subj_group}"	
		echo "\
\
#!/bin/sh

#SBATCH --job-name=dual_reg_d${dim}
#SBATCH --output=${ICA_dir}/logs/dual_reg_d${dim}.out
#SBATCH --error=${ICA_dir}/logs/dual_reg_d${dim}.err
#SBATCH --time=05:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --mem=50gb

# constants
base_dir=\"/scratch/tyoeasley/WAPIAW3\"
mask_fpath=\"\${base_dir}/brainrep_data/final_GM_mask.nii.gz\" 
mk_descon=\"\${base_dir}/brainrep_data/ICA_data/rand_design_con.py\"
mk_flist=\"\${base_dir}/brainrep_data/eid_to_fpath.sh\"
fpath_pattern=\"/ceph/biobank/derivatives/melodic/sub-%s/ses-01/sub-%s_ses-01_melodic.ica/filtered_func_data_clean_MNI152.nii.gz\"

# user specifications
dim=${dim}
design_fpath_type=\"\${base_dir}/brainrep_data/ICA_data/design${dim}\"
eid_list=${subj_group}

# derivatives
outname=\$( basename \${eid_list} | cut -d. -f 1)
melodic_out=\"\${base_dir}/brainrep_data/ICA_data/melodic_output/\${outname}/ica\${dim}\"
DR_out=\${melodic_out/\"melodic_output\"/\"dual_regression\"}
data_flist=\"\${base_dir}/brainrep_data/ICA_data/raw_data_subj_lists/\${outname}.txt\"
\${mk_flist} -i \${eid_list} -o \${data_flist} -p \${fpath_pattern}
n_subj=\$(cat \${data_flist} | wc -l )

python \${mk_descon} -n \${n_subj} --fpath_noext \${design_fpath_type}

# output
echo \"pulling from subject list: \${eid_list}\"
echo \"pulling subject data from generalized filepath: \${fpath_pattern}\"
echo \"        (list of filenames of preprocessed data can be found in): \${data_flist}\"
echo \"computing with \${dim} dimensions\"
echo \"sending melodic outputs to: \${melodic_out}\"
if ! [ -d \${melodic_out} ]
then
	mkdir -p \${melodic_out}
fi
echo \"sending dual_regression outputs to: \${DR_out}\"
if ! [ -d \${DR_out}/groupICA\${dim}.dr ]
then
	mkdir -p \${DR_out}
fi
# FSL calls
module load fsl
export DISPLAY=:1

melodic -i \${data_flist} -o \${melodic_out} --tr=0.72 --nobet -a concat -m \${mask_fpath} --report --Oall -d \${dim}

FSL_slurm/dual_regression_slurm \"\${melodic_out}/melodic_IC.nii.gz\" \${dim} \"\${design_fpath_type}.mat\" \"\${design_fpath_type}.con\" 0 \"\${DR_out}/groupICA\${dim}.dr\" \$(cat \${data_flist})
\
" > "${sbatch_fpath}"  

		# Overwrite submission script# Make script executable
		chmod +x "${sbatch_fpath}" || { echo "Error changing the script permission!"; exit 1; }

    		# Submit script
    		sbatch "${sbatch_fpath}" || { echo "Error submitting jobs!"; exit 1; }
	done
	echo "Waiting between dimension calls to avoid *stepping on toes*..."
	sleep 15
	echo "Done."
done

