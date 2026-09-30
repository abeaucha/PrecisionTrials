

import precision_trials.datasets.core as dat 
import precision_trials.datasets.imaging as img
import precision_trials.datasets.behaviour as beh
import precision_trials.datasets.genetics as gen


es = img.EffectSizeImages()

jac = img.JacobianImages()

t1 = img.T1wImages()


behv = beh.BehaviourTest()
gent = gen.GeneticsTest()

imgdat = dat.ImagingDataset()
behdat = dat.BehaviourDataset()
gendat = dat.GeneticsDataset()


dataset = dat.ParticipantDataset()
dataset.imaging.add(es, jac, t1)


dat.ParticipantDataset(imaging = dat.ImagingDataset(es, jac, t1))
dat.ParticipantDataset(imaging = dat.BehaviourDataset(behv))

dat.ParticipantDataset()

print()