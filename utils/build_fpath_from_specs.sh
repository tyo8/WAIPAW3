brainrep=${1:-ICA300}
groupname=${2:-example}
feature=${2:-Amplitudes}

base_dir=/scratch/tyoeasley/WAPIAW3/brain_data

case $brainrep in

	PROFUMO)
		dim=$(expr brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type="${base_dir}/PROFUMO_data/out_PROFUMO/d${dim}_${groupname}.pfm/${feature}/sub-%s.csv"
		;;
	
	ICA)
		dim=$(expr brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type="${base_dir}/ICA_data/dual_regression/${groupname}/ica${dim}/${feature}/sub-%s.csv"
		ext=%s
		;;

	schaefer)
		dim=$(expr brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type=????
		;;
	grad)
		dim=$(expr brainrep : "[^0-9]*\([0-9]*\)")
		datapath_type=????
		;;
esac

echo $datapath_type
