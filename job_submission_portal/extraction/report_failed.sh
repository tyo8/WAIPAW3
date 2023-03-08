verbose=${1:-false}
log_dir=${2:-"/scratch/tyoeasley/WAPIAW3/job_submission_portal/extraction/brainrep_xtr_scripts/logs"}

errpath_list=$( ls ${log_dir}/*.err )
for errpath in $errpath_list
do

        if [[ $( stat --printf=%s $errpath ) -gt 0 ]]
        then
                echo "found nonempty error message in ${errpath}"
                if $verbose
                then
                        echo "           errmsg:"
                        cat $errpath
                        printf "\n\n"
                fi
        fi
done
