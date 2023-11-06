#!/bin/bash

set -o nounset

basedir="/scratch/tyoeasley/WAPIAW3/brainrep_data/ICA_data"
groupname="rmed_G45_eid_wapiaw"
dim=25

# to automatically find these parameters so that they no longer have to be give as input:
# look for sharp and wide differences between clusters of dates. Start w search for large difference between first and last day. (MEDIUM)
early_start="2023-06-02"
late_start="2023-06-13"

while getopts ":g:d:" opt; do
  case $opt in
    g) groupname="${OPTARG}"
    ;;
    d) dim=${OPTARG}
    ;;
    E) early_start=${OPTARG}
    ;;
    L) late_start=${OPTARG}
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

brainrep="ICA${dim}"

# build data dir from groupname and dimension parameters
datadir="${basedir}/dual_regression/${groupname}/ica${dim}/groupICA${dim}.dr"
# name generic output file
outfile="${basedir}/early_vs_late_extractions_eids/${brainrep}_${groupname}"

### check extraction dates for large gap
# first day of data extraction
# last day of data extraction
# time elapsed between first and last day? (is it easy/possible to find files with "smallest difference in mod dates >=2 days" or smthn?)

### check masks
# check that maskALL is made after latest dr_stage_1 file (is this actually the right relative timing???) (EASY)
# compare also to per-subject mask dates, just to be safe (EASY)

early_end=$(date +%Y-%m-%d -d "${early_start} + 1 day")
late_end=$(date +%Y-%m-%d -d "${late_start} + 1 day")

# group extracted data by date cluster
find "${datadir}/dr_stage1_"* -type f -newermt ${early_start} ! ${early_end} | cut -d_ -f 3 | cupt -d. -f1 > "${outfile}_early"
find "${datadir}/dr_stage1_"* -type f -newermt ${late_start} ! ${late_end} | cut -d_ -f 3 | cupt -d. -f1 > "${outfile}_late"

### pull from extraction completion-checking code:
### check percentage overlap between date cluster lists and patient/control lists (by date cluster) (MEDIUM)
# what is the total number of different subjects extracted vs. total number of subjects in group?
# what percentage of all subjects were extracted on first extraction day vs. what percentage on last extraction day?
# what percentage of subjects extracted on first ext day were patients vs. controls?
# what percentage of subjects extracted on last ext day were patients vs. controls?

