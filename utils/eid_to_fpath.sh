#!/bin/bash

set -o nounset

# (input) filepath to list of subject eids
input_eids="/scratch/tyoeasley/WAPIAW3/subject_lists/example.txt"

# (output) filepath in which to store list of subject filepaths
output_fpath="/scratch/tyoeasley/WAPIAW3/brainrep_data/ICA_data/raw_data_subj_lists/example.txt"

# printf-ready pattern waiting to substitue eid numbers as string literals to specify filepath to subject-level data
pattern="/ceph/biobank/derivatives/melodic/sub-%s/ses-01/sub-%s_ses-01_melodic.ica/filtered_func_data_clean_MNI152.nii.gz"

### argument parsing ###
while getopts ":i:o:p:" opt; do
  case $opt in
    i) input_eids=${OPTARG}
    ;;
    o) output_fpath=${OPTARG}
    ;;
    p) pattern=${OPTARG}
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

# count number of per-pattern eid substitutions that need to be made
n_substs=$(grep "%s" -o <<< ${pattern} | wc -l)

# remove existing ${output_fpath} (if it exists) to avoid re-appending to it
if ! compgen -G "${output_fpath}" >> /dev/null
then
	# append a data filepath to ${output_fpath} for every eid in ${input_eids}
	for eid in $(cat ${input_eids});
	do
		# creates eid-string substitution input to correctly fill out the given filepath pattern
		inp_str=$( printf "%0.s ${eid}" $(seq 1 ${n_substs}) )

		# saves newline-appended filepath to the output list
		printf "${pattern}\n" ${inp_str} >> ${output_fpath}
	done

	cat ${output_fpath} | sort | uniq > "tmp_${output_fpath}"
	mv "tmp_${output_fpath}" ${output_fpath}
fi
