#!/bin/bash

set -o nounset

# (input) filepath to list of subject eids
input_fpath=${1:-""}

# piped commands contain redundant find&remove of substring "sub-" to ensure found number is eid
eid=$(echo $input_fpath | egrep -o 'sub-[[:digit:]]{7}' | head -1 | cut -d- -f 2)

echo $eid
