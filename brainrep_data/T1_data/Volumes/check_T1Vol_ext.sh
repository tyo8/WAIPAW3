set -o nounset

datadir=${1:-"/scratch/tyoeasley/WAPIAW3/brainrep_data/T1_data/Volumes"}
n_show=25

# full_list=/scratch/tyoeasley/WAPIAW3/subject_lists/combined_subj_eid/age_list_large.csv
full_list=/scratch/tyoeasley/WAPIAW3/subject_lists/all_subj_eid.csv
done_list=/scratch/tyoeasley/WAPIAW3/brainrep_data/T1_data/Volumes/completed_subjs.csv
todo_list=/scratch/tyoeasley/WAPIAW3/brainrep_data/T1_data/Volumes/incomplete_subjs.csv

rm $done_list
ls ${datadir} | cut -d- -f 2 | cut -d. -f 1 | cut -d_ -f 1 | sort > ${done_list}


comm ${full_list} ${done_list} -23 --check-order > ${todo_list}

n_todo=$( cat $todo_list| wc -l )
echo "A total of $n_todo subjects are missing T1 Volume $( basename $datadir ) data."

if [[ "${n_todo}" -gt 0 ]]
then
	echo "The following subjects are missing T1 Volume data:"
	cat $todo_list | head -${n_show}
	if [[ "${n_todo}" -gt "${n_show}" ]]
	then
		echo "... (only the first ${n_show} subject IDs are displayed here)"
	fi
fi
