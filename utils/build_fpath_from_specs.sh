groupname=${1:-example}
brainrep=${2:-ICA300}
feature=${3:-Amplitudes}

base_dir=/scratch/tyoeasley/WAPIAW3/brainrep_data

case $brainrep in

	PROFUMO)
		dim=$(expr brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type="${base_dir}/PROFUMO_data/out_PROFUMO/${groupname}_${dim}.pfm/${feature}/sub-%s.csv"
		;;
	
	ICA)
		dim=$(expr brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type="${base_dir}/ICA_data/dual_regression/${groupname}/ica${dim}/${feature}/sub-%s.csv"
		;;

	Schaefer)
		dim=$(expr brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type="${base_dir}/Schaefer_data/${feature}/sub-%s.csv"
		;;
	grad)
		dim=$(expr brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type="${base_dir}/diffusion_gradient_data/features/${groupname}/${feature}/sub-%s_emb.csv"
		;;
esac

echo $datapath_type
