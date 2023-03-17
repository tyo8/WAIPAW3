n_subj=${1:-254}
subj_path_type=${2:-"/scratch/tyoeasley/WAPIAW3/brainrep_data/gradient_data/subj_gradients/sub-%s_emb.csv"}

# at 1KB per subject and 254 subjects, we estimate our memory usage at ~700MB
mem_growth_factor=$(( 700*1024*/254 ))

samp_subj_ID="1061708"
samp_subj_path="${subj_path_type/%s/samp_subj_ID}"
samp_subj_mem=$( stat --printf="%s" ${samp_subj_path} )
