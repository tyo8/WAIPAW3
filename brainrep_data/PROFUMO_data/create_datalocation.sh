#!/bin/sh

set -u nounset

base_dir="/scratch/tyoeasley/WAPIAW3"
subj_list="/scratch/tyoeasley/WAPIAW3/subject_lists/example.txt"
js_fname_type="\$( echo \"/scratch/tyoeasley/WAPIAW3/brainrep_data/PROFUMO_data/raw_data_subj_lists/${groupname}_datalocations.json\" )"


while getopts ":b:s:j:" opt; do
  case $opt in
    b) base_dir=${OPTARG}
    ;;
    s) subj_list=${OPTARG}
    ;;
    j) js_fname_type=${OPTARG}
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
groupname=$( basename ${eid_list} | cut -d. -f 1)
js_fname=$( eval ${js_fname_type} )

n_subj=$( wc ${subj_list} | cut -d' ' -f 1 )

# overwrite/create json file and make first bracket
printf "{\n" > ${js_fname}
counter=0
for i in `cat ${subj_list}` ; do
        let counter=counter+1
	# echo ${counter}
        subj_name="sub-${i}"
        # print subject identifier
        printf "\t\"${subj_name}\": {\n" >> ${js_fname}
        # print data location
        data_loc=/ceph/biobank/derivatives/melodic/sub-${i}/ses-01/sub-${i}_ses-01_melodic.ica/filtered_func_data_clean_MNI152.nii.gz
        printf "\t\t\"ses\": \"${data_loc}\"" >> ${js_fname}
        printf "\n\t}" >> ${js_fname}
        # check for comma placement
	if [[ "${counter}" -lt "${n_subj}" ]]
	then
		printf "," >> ${js_fname}
		### debug code ###
		# echo "we are in the if statement and have satisfied counter < n_subj: counter=${counter}, n_subj=${n_subj}"
		### debug code ###
	else
		### debug code ###
		# echo "we are in the if statement and have satisfied counter >= n_subj: counter=${counter}, n_subj=${n_subj}"
		### debug code ###
	fi
	printf "\n" >> ${js_fname}
done

# close last bracket in json
printf "\n}" >> $js_fname

echo $js_fname
