
import precision_trials.datasets.core as dat
from precision_trials.datasets.imaging import EffectSizeImages
from precision_trials.evidence import AHBADecodingModule

import pandas as pd

if __name__ == '__main__':

    dataset = dat.ParticipantDataset(
        imaging = dat.ImagingDataset(
            EffectSizeImages(jacobian_type="relative")
        )
    )

    AHBA_module = AHBADecodingModule()

    AHBA_module.run(dataset, n_files = 5, n_jobs = 1)


    correlations = AHBA_module.correlations

    df_correlations = pd.DataFrame(correlations, index = pd.Index(AHBA_module.genes, name = "gene"))
    
    df_image_files = pd.DataFrame({'file': AHBA_module.image_files})

    df_correlations.to_csv("AHBA_decoding_correlations.csv")
    df_image_files.to_csv("AHBA_decoding_image_files.csv", index=False)


    print()



    