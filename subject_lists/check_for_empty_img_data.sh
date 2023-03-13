set -o nounset

subj_list_fname=${1:-"/scratch/tyoeasley/WAPIAW3/subject_lists/all_subj_eid.csv"}
subj_list=$( cat $subj_list_fname )

for eid in $subj_list
do
	fpath="/ceph/biobank/derivatives/melodic/sub-${eid}/ses-01/sub-${eid}_ses-01_melodic.ica/filtered_func_data_clean_MNI152.nii.gz"

	if ! [[ $( stat --printf=%s $fpath ) -gt 0 ]]
	then
		echo $eid >> empty_melodic_data_eid.txt
	fi
done
