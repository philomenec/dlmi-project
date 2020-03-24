

#import os 
#os.chdir("C:/Users/Philo/Documents/3A -- MVA/DL for medical imaging/retine/dlmi-project")
#os.getcwd()


import torch
import numpy as np

# import general configuration
#from config import * #doesn't work

torch.random.manual_seed(0)
np.random.seed(0)

DRIVE_SUBSET_TRAIN = slice(0, 15)
DRIVE_SUBSET_VAL = slice(15, 23)

STARE_SUBSET_TRAIN = slice(0, 15)
STARE_SUBSET_VAL = slice(15, 21)

ARIA_SUBSET_TRAIN = slice(0, 107)
ARIA_SUBSET_VAL = slice(107, 143)

# Input image resolution
PATCH_SIZE = 320

GAMMA_CORRECTION = 1.2



### Test bools
test_in_train = True
test_in_net = False

### Training params
epochs = 4
batch_size = 5
#batch_size = 2
#batch_size = 1

model = "InterraterNet"

lr = 1e-3
loss = "MSE"

validate_every = 1
dataset = "STARE"

#transforms_name = "None"
transforms_name = "make_train_transform"
#transforms_name = "make_basic_train_transform"