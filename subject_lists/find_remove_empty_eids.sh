#!/bin/sh

delete=${1:-false}
eid_dir=${2:-"/scratch/tyoeasley/WAPIAW3/subject_lists/patient_eid_sandbox"}

empty_eid_file="/scratch/tyoeasley/WAPIAW3/subject_lists/empty_melodic_data_eid.txt"


for eid in $( cat ${empty_eid_file} )
do
	out=$( grep -nw ${eid_dir}/* -e ${eid} )
	for line in $out
	do
		echo $line
		if $delete
		then
			fpath=$( echo $line | cut -d: -f 1 )
			echo "removing ${eid} from ${fpath}"
			mv ${fpath} ${fpath}_new
			grep -vw ${fpath}_new -e ${eid} > ${fpath}
			rm ${fpath}_new
		fi
	done
done
