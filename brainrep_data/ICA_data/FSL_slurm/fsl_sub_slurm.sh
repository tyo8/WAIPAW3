#!/bin/bash

# NOTE: list of differences with respect to classic fsl_sub, all of which need to be adjusted on call-side
# (1) -j functionality does not key to a specific job; rather, it requires the *submitted* job to terminate before exit (also newly requires argument, e.g. -j true )
# (2) there is no flag option to mimic -t functionality; instead, submit instances of a job via the same submission file overwritten with new parameters (e.g., within a loop rather than external to it)
# (3) decided to use -f flag to specify input file; no longer a positional argument

set -o nounset

sbatch_fname="test.sh"

sequential_run=false
maxtime_str="123:55:00"
job_name="fsl_dr-ica"
log_dir="/scratch/tyoeasley/WAPIAW3/brainrep_data/ICA_data/FSL_slurm/logs"
mem_gb=50
partition="small"

while getopts ":j:T:N:l:g:p:f:" opt; do
  case $opt in
    j) sequential_run=${OPTARG}
    ;;
    T) maxtime_str="${OPTARG}:00:00"
    ;;
    N) job_name=${OPTARG}
    ;;
    l) log_dir=${OPTARG}
    ;;
    g) mem_gp=${OPTARG}
    ;;
    p) partition=${OPTARG}
    ;;
    f) sbatch_fname=${OPTARG}
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


########################## Write the parameters and the script #########################

# do not append an extra header:
first_line=$(cat ${sbatch_fname} | head -1)
if [[ ${first_line} != *"bin/sh"* ]]
then
	cp ${sbatch_fname} "${sbatch_fname}_tmp"
	rm ${sbatch_fname}
	echo "\
\
#!/bin/sh

#SBATCH --job-name=\"${job_name}\"
#SBATCH --output=\"${log_dir}/${job_name}.out%j\"
#SBATCH --error=\"${log_dir}/${job_name}.err%j\"
#SBATCH --partition=${partition}
#SBATCH --time=${maxtime_str}
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --mem=${mem_gb}gb

\
	" > ${sbatch_fname}
	cat "${sbatch_fname}_tmp" >> ${sbatch_fname}
	rm "${sbatch_fname}_tmp"
fi

# Make script executable
chmod 771 "${sbatch_fname}" || { echo "Error changing the script permission!"; exit 1; }

# Submit script
if [[ $sequential_run == true ]]
then
	sbatch --wait "${sbatch_fname}" || { echo "Error submitting jobs!"; exit 1; }
else
	sbatch "${sbatch_fname}" || { echo "Error submitting jobs!"; exit 1; }
fi

