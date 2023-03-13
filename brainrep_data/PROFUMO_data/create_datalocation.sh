#!/bin/sh

set -o nounset


base_dir="/scratch/tyoeasley/WAPIAW3"
subj_list="/scratch/tyoeasley/WAPIAW3/subject_lists/example.txt"
js_fpath="/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/raw_data_subj_lists/example_datalocations.json"

while getopts ":b:s:j:" opt; do
  case $opt in
    b) base_dir=${OPTARG}
    ;;
    s) subj_list=${OPTARG}
    ;;
    j) js_fpath=${OPTARG}
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

groupname=$( basename ${subj_list} | cut -d. -f 1)

n_subj=$( cat ${subj_list} | wc -l ) 

echo ""
echo "Sending raw data locations for ${groupname} (has ${n_subj} subjects) to ${js_fpath}..."

# overwrite/create json file and make first bracket
printf "{\n" > ${js_fpath}
counter=0
for i in $( cat ${subj_list} )
do
        let counter=counter+1
        subj_name="sub-${i}"
        # print subject identifier
        printf "\t\"${subj_name}\": {\n" >> ${js_fpath}
        # print data location
        data_loc="/ceph/biobank/derivatives/melodic/sub-${i}/ses-01/sub-${i}_ses-01_melodic.ica/filtered_func_data_clean_MNI152.nii.gz"
        printf "\t\t\"ses\": \"${data_loc}\"" >> ${js_fpath}
        printf "\n\t}" >> ${js_fpath}
        # check for comma placement

	### debug code ### (comma placement) 
	printf "subject ${counter} of ${n_subj} added to .json source file\n"
	### debug code ### (comma placement) 

	if [[ "${counter}" -lt "${n_subj}" ]]
	then
		printf "," >> ${js_fpath}
	fi
	printf "\n" >> ${js_fpath}
done

# close last bracket in json
printf "\n}" >> ${js_fpath}

echo "Sent raw data locations for ${groupname} to ${js_fpath}"
echo ""
