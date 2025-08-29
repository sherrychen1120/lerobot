# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import cv2
from typing import Any

import numpy as np
import rerun as rr


def _init_rerun(session_name: str = "lerobot_control_loop") -> None:
    """Initializes the Rerun SDK for visualizing the control loop."""
    batch_size = os.getenv("RERUN_FLUSH_NUM_BYTES", "8000")
    os.environ["RERUN_FLUSH_NUM_BYTES"] = batch_size
    rr.init(session_name)
    memory_limit = os.getenv("LEROBOT_RERUN_MEMORY_LIMIT", "10%")
    rr.spawn(memory_limit=memory_limit)


def log_rerun_data(observation: dict[str | Any], action: dict[str | Any]):
    for obs, val in observation.items():
        if isinstance(val, float):
            rr.log(f"observation.{obs}", rr.Scalar(val))
        elif isinstance(val, np.ndarray):
            if val.ndim == 1:
                for i, v in enumerate(val):
                    rr.log(f"observation.{obs}_{i}", rr.Scalar(float(v)))
            else:
                rr.log(f"observation.{obs}", rr.Image(val), static=True)
    for act, val in action.items():
        if isinstance(val, float):
            rr.log(f"action.{act}", rr.Scalar(val))
        elif isinstance(val, np.ndarray):
            for i, v in enumerate(val):
                rr.log(f"action.{act}_{i}", rr.Scalar(float(v)))

def visualize_camera_feeds(observation: dict[str, Any]):
    for cam_key, cam_val in observation.items():
        if not cam_key.startswith("cam_"):
            continue
        if cam_key.endswith("_timestamp"):
            continue
        
        # Skip if not a valid image array
        if not isinstance(cam_val, np.ndarray):
            print(f"  Skipping {cam_key}: not a numpy array")
            continue
        
        if len(cam_val.shape) != 3:
            print(f"  Skipping {cam_key}: invalid shape {cam_val.shape}")
            continue
        
        # Convert image format if needed
        display_img = cam_val.copy()
        
        # Handle different data types and ranges
        if cam_val.dtype == np.float32 or cam_val.dtype == np.float64:
            if cam_val.max() <= 1.0:
                # Assume normalized [0,1] range, convert to [0,255]
                display_img = (display_img * 255).astype(np.uint8)
            else:
                # Assume already in [0,255] range but float
                display_img = display_img.astype(np.uint8)
        
        # Convert RGB to BGR for OpenCV (if needed)
        if display_img.shape[2] == 3:
            # OpenCV expects BGR, but many cameras provide RGB
            display_img = cv2.cvtColor(display_img, cv2.COLOR_RGB2BGR)
        
        # Modify image stream to match teleoperator POV.
        # TODO(sherry): Make this configurable in RecordConfig.
        if cam_key == "cam_top":
            display_img = cv2.rotate(display_img, cv2.ROTATE_90_CLOCKWISE)
        elif cam_key == "cam_front":
            display_img = cv2.flip(display_img, 1)
        
        cv2.imshow(cam_key, display_img)
    
    # Process OpenCV events to update display windows
    cv2.waitKey(1)
