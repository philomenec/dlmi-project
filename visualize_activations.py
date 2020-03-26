"""Perform inference on an exemple, and get the resulting activation maps."""
import numpy as np
import torch
from torchvision.utils import make_grid
from nets import MODEL_DICT
from utils.interpretation import DownBlockActivations
from utils import load_preprocess_image

import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import config
from config import PATCH_SIZE

from typing import List
import json
import argparse

with open("dataset_statistics.json") as f:
    dataset_stats_ = json.load(f)


if torch.cuda.is_available():
    from torch.backends import cudnn
    cudnn.benchmark = True
    DEVICE = "cuda"
else:
    DEVICE = "cpu"


parser = argparse.ArgumentParser(
    "visualize-activations",
    description="Visualize activations in feature maps.")
parser.add_argument("--weights", help="Path to model weights.")
parser.add_argument("--img", type=str,
                    help="Image to run the model on.", required=True)

parser.add_argument("--model", choices=MODEL_DICT.keys())
parser.add_argument("--gray", type=bool, default=True,
                    help="Whether to load the image in grayscale, and apply appropriate model. (default %(default)s)")
parser.add_argument("--antialias", action='store_true',
                    help="Use model with anti-aliased max pooling operator.")
parser.add_argument("--save-path", type=str,
                    help="Save the maps to a file.")

args = parser.parse_args()

num_channels = 1 if args.gray else 3

_kwargs = {
    'num_channels': num_channels,
    'antialias': args.antialias
}

print("Model class: {:s}".format(args.model))
model_cls = MODEL_DICT[args.model]

model = model_cls(**_kwargs)

if args.weights is not None:
    state_dict = torch.load(args.weights)
    model.load_state_dict(state_dict['model_state_dict'])
else:
    import warnings
    warnings.warn("Model weights not loaded.")
model.to(DEVICE)


img, img_t = load_preprocess_image(args.img, gray=args.gray)
img_t = img_t.to(DEVICE)
input_size = img.shape[:2]
viz_ = DownBlockActivations(model, down_kw=['down1', 'down2', 'down3'])

# Perform prediction

with torch.no_grad():
    prediction_ = model(img_t)
    probas_ = torch.softmax(prediction_, dim=1)
    prediction_ = prediction_.data.cpu().numpy()[0, 1]
    probas_ = probas_.data.cpu().numpy()[0, 1]

# Plotting logic

# fig: plt.Figure = plt.figure(figsize=(8, 5))

# ax = fig.add_subplot(1, 2, 1)
# ax.imshow(img)
# ax.set_title("Initial image")
# ax.axis('off')

# ax = fig.add_subplot(1, 2, 2)
# ax.imshow(probas_)
# ax.set_title("Proba map")
# ax.axis('off')
# fig.tight_layout()


for idx, (name, arr) in enumerate(viz_.get_maps(img_t)):
    print(name, arr.shape)
    num_feats_ = arr.shape[1]
    num_rows_mul = num_feats_ // 128
    arr_grid = make_grid(arr.transpose(0, 1), nrow=16, padding=0,
                         normalize=True, scale_each=True)
    arr_grid = arr_grid[0]
    print("grid:", arr_grid.shape)

    fig: plt.Figure = plt.figure(figsize=(10, num_rows_mul * 5), dpi=100)
    ax = fig.add_subplot()
    ims_ = ax.imshow(arr_grid, cmap='viridis')
    ax.set_title("Activations: {:s}".format(name))
    ax.axis('off')
    fig.tight_layout()
    
    if args.save_path is not None:
        fig.savefig("{:s}_{:s}.png".format(args.save_path, name))


plt.show()