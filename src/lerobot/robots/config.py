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

import abc
import json
from dataclasses import dataclass
from pathlib import Path

import draccus

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.realsense.configuration_realsense import RealSenseCameraConfig

@dataclass(kw_only=True)
class RobotConfig(draccus.ChoiceRegistry, abc.ABC):
    # Allows to distinguish between different robots of the same type
    id: str | None = None
    # Directory to store calibration file
    calibration_dir: Path | None = None
# Path to JSON file containing camera configurations
    camera_configs_path: Path | None = None

    def __post_init__(self):
        # Only one of cameras and camera_configs_path should be provided.
        if len(self.cameras) > 0 and self.camera_configs_path is not None:
            raise ValueError("Only one of cameras and camera_configs_path can be provided.")
        
        # Load cameras from JSON file if path is provided
        if self.camera_configs_path is not None:
            self._load_camera_configs_from_json()
        
        if hasattr(self, "cameras") and self.cameras:
            for _, config in self.cameras.items():
                for attr in ["width", "height", "fps"]:
                    if getattr(config, attr) is None:
                        raise ValueError(
                            f"Specifying '{attr}' is required for the camera to be used in a robot"
                        )

    def _load_camera_configs_from_json(self):
        """Load camera configurations from JSON file."""
        
        config_path = Path(self.camera_configs_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Camera configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                cameras_config_dict = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in camera configuration file {config_path}: {e}")
        
        if not isinstance(cameras_config_dict, dict):
            raise ValueError(f"Camera configuration file must contain a JSON object, got {type(cameras_data).__name__}")
        
        # Convert JSON data to CameraConfig objects
        cameras = {}
        for camera_name, raw_config in cameras_config_dict.items():
            if not isinstance(raw_config, dict):
                raise ValueError(f"Camera '{camera_name}' configuration must be a dictionary")
            
            camera_type = raw_config.get("type")
            if camera_type is None:
                raise ValueError(f"Camera '{camera_name}' must specify a 'type'")
            
            # Create the appropriate camera config object based on type
            # Remove 'type' key from config dict before passing to constructor
            config_without_type = {k: v for k, v in raw_config.items() if k != "type"}
            
            if camera_type == "opencv":
                cameras[camera_name] = OpenCVCameraConfig(**config_without_type)
            elif camera_type == "realsense":
                cameras[camera_name] = RealSenseCameraConfig(**config_without_type)
            else:
                raise ValueError(f"Unsupported camera type '{camera_type}' for camera '{camera_name}'")
        
        # Set the cameras attribute if it exists
        if hasattr(self, "cameras"):
            self.cameras = cameras
        else:
            raise ValueError("Robot configuration does not support cameras")

    @property
    def type(self) -> str:
        return self.get_choice_name(self.__class__)
