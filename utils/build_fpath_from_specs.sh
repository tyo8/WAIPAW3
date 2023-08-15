groupname=${1:-example}
brainrep=${2:-ICA300}
feature=${3:-Amplitudes}

base_dir="/scratch/tyoeasley/WAPIAW3/brainrep_data"

case $brainrep in

	PROFUMO*)
		dim=$(expr $brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type="${base_dir}/${brainrep}_data/out_PROFUMO/${groupname}_${dim}_Results.ppp/${feature}/sub-%s.csv"
		;;
	
	ICA*)
		dim=$(expr $brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type="${base_dir}/ICA_data/dual_regression/${groupname}/ica${dim}/${feature}/sub-%s.csv"
		;;

	Schaefer)
		dim=$(expr $brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type="${base_dir}/${brainrep}_data/${feature}/sub-%s.csv"
		;;
	gradient)
		# EXPECTS DIFFERENT PIPELINE THAN OTHER BRAINREPS: NEED TO DO GROUP ALIGNMENT BEFORE PREDICTION!
		dim=$(expr $brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type="${base_dir}/diffusion_gradient_data/subj_gradients/sub-%s_emb.csv"
		group_datapath_type="${base_dir}/${brainrep}_data/group_gradients/${groupname}_emb.csv"
		echo ${group_datapath_type}
		;;
	T1)
		datapath_type="${base_dir}/${brainrep}_data/${feature}/sub-%s.csv"
		;;
	SocialDemo)
                datapath_type="${base_dir}/${brainrep}_data/${feature}/sub-%s.csv"
                ;;
esac

echo $datapath_type
