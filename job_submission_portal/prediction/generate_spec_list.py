import argparse

brainrep_types = ['ICA', 'PROFUMO', 'Schaefer', 'gradient']
ICA_dims = [25, 100, 150, 300]
ICA_feats = ['Amplitudes', 'NetMats', 'partial_NMs']
PROFUMO_dims = [25, 150]
PROFUMO_feats = ['Maps', 'NetMats', 'spatial_NMs']
Schaefer_dims = [400]
Schaefer_feats = ['NetMats', 'Amplitudes', 'partial_NMs']
gradient_dims = [40]
gradient_feats = ['Maps']


def write_line(spec_line, output):
        with open(output,'a') as fout:
            fout.write(spec_line + '\n')


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="generate specification list for prediction submitter")
    parser.add_argument(
            '-o',
            '--output',
            type=str,
            default="spec_list_full.txt",
            help="write spec_list.txt to given filepath"
            )
    args=parser.parse_args()
    with open(args.output, 'w') as fout:
        fout.write('')

    for brainrep in brainrep_types:
        if "ICA" in brainrep:
            for dim in ICA_dims:
                for feat in ICA_feats:
                    spec_line = f"ICA{dim}_{feat}"
                    write_line(spec_line, args.output)
        elif "PROFUMO" in brainrep:
            for dim in PROFUMO_dims:
                for feat in PROFUMO_feats:
                    spec_line = f"PROFUMO{dim}_{feat}"
                    write_line(spec_line, args.output)
        elif "Schaefer" in brainrep:
            for dim in Schaefer_dims:
                for feat in Schaefer_feats:
                    spec_line = f"Schaefer{dim}_{feat}"
                    write_line(spec_line, args.output)
        elif "gradient" in brainrep:
            for dim in gradient_dims:
                for feat in gradient_feats:
                    spec_line = f"gradient{dim}_{feat}"
                    write_line(spec_line, args.output)
        else:
            spec_line = "INVALID SPEC: " + brainrep
            write_line(spec_line, args.output)

