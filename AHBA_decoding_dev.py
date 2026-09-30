
import precision_trials.datasets.core as dat
from precision_trials.datasets.imaging import EffectSizeImages
from precision_trials.evidence import AHBADecodingModule


if __name__ == '__main__':

    dataset = dat.ParticipantDataset(
        imaging = dat.ImagingDataset(
            EffectSizeImages(jacobian_type="relative")
        )
    )

    AHBA_module = AHBADecodingModule()

    AHBA_module.run(dataset, n_files = 50, n_jobs = 1)

    print()



    