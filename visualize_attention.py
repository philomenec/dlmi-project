"""Perform inference on an example and visualize the attention maps."""
import numpy as np
import torch
from nets import AttentionUNet
from utils.interpretation import AttentionMapHook
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
    "visualize-attention",
    description="Visualize attention maps of the Attention U-Net model.")
parser.add_argument("--weights", help="Path to model weights.")
parser.add_argument("--img", type=str, help="Image to run the model on.", required=True)

parser.add_argument("--gray", type=bool, default=True,
                    help="Whether to load the image in grayscale, and apply appropriate model. (default %(default)s)")
parser.add_argument("--antialias", action='store_true',
                    help="Use model with anti-aliased max pooling operator.")

args = parser.parse_args()

num_channels = 1 if args.gray else 3

_kwargs = {
    'num_channels': num_channels,
    'antialias': args.antialias
}

model = AttentionUNet(**_kwargs)
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
att_viz = AttentionMapHook(model, upscale=True, input_size=input_size)

# Perform prediction

with torch.no_grad():
    prediction_ = model(img_t)
    probas_ = torch.softmax(prediction_, dim=1)
    prediction_ = prediction_.data.cpu().numpy()[0, 1]
    probas_ = probas_.data.cpu().numpy()[0, 1]

# Plotting logic

fig: plt.Figure = plt.figure(figsize=(7, 8))
gs = fig.add_gridspec(3, 4)

ax = fig.add_subplot(gs[0, :2])
ax.imshow(img)
ax.set_title("Initial image")
ax.axis('off')

ax = fig.add_subplot(gs[0, 2:])
# ax.imshow(prediction_)
# ax.set_title("Network output")
# ax.axis('off')

# ax = fig.add_subplot(gs[0, 3])
ax.imshow(probas_)
ax.set_title("Proba map")
ax.axis('off')

for idx, (name, arr) in enumerate(att_viz.get_maps()):
    i_loc = 2 * idx + 4
    arr = arr[0, 0]
    ax = fig.add_subplot(gs[i_loc:i_loc+2])
    ims_ = ax.imshow(arr, cmap='viridis')
    ax.set_title("Attention Map: {:s}".format(name))
    ax.axis('off')
    # Plot colorbar on 1st map
    if idx==0:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        plt.colorbar(ims_, cax=cax)


fig.tight_layout()
plt.show()

