
import precision_trials.datasets.core as dat
from precision_trials.datasets.imaging import EffectSizeImages
from precision_trials.evidence import AHBADecodingModule


dataset = dat.ParticipantDataset(
    imaging = dat.ImagingDataset(
        EffectSizeImages(jacobian_type="relative")
    )
)

AHBA_module = AHBADecodingModule()

AHBA_module.run(dataset)

print()