#!/bin/sh

set -o nounset

input_pattern="/scratch/tyoeasley/WAPIAW3/brainrep_data/ICA_data/dual_regression/example/ica25/groupICA25.dr/dr_stage1_"
group_fpath="/scratch/tyoeasley/WAPIAW3/subject_lists/match_eid/example.csv"
outfile="/dev/null"
msg="matching patterns found"
eval_if_empty="echo \"\""

while getopts ":i:g:o:m:e:" opt; do
  case $opt in
    i) input_pattern=${OPTARG}
    ;;
    g) group_fpath="${OPTARG}"
    ;;
    o) outfile=${OPTARG}
    ;;
    m) msg=${OPTARG}
    ;;
    e) eval_if_empty=${OPTARG}
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

total=$( cat ${group_fpath} | wc -l )
if compgen -G ${input_pattern}* > /dev/null     
then
	found=$(ls ${input_pattern}* | wc -l )
else
	found=0
	eval ${eval_if_empty}
fi
perc=$(( 100*${found}/${total} ))  
if [[ "${perc}" -lt "100" ]]
then
	if [[ ${msg} == "matching patterns found" ]]
	then
		echo "${input_pattern}: ${perc}% ${msg} (${found} of ${total} total)"
	else
		echo "$( dirname ${input_pattern} ): ${perc}% ${msg} (${found} of ${total} total)"
	fi
	echo "${group_fpath}" >> "${outfile}"
fi
