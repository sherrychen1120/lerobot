#!/usr/bin/env python

# Example of running a specific test:
# ```bash
# pytest tests/cameras/test_camera_config.py::test_json_camera_config
# ```

import pytest

from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig

def test_json_camera_config():
    """Test loading camera config from JSON file."""
    print("Testing JSON camera configuration loading...")
    
    # Test with JSON file
    config = SO101FollowerConfig(
        port="/dev/test",
        camera_configs_path="example_camera_config.json"
    )
    
    print(f"Loaded {len(config.cameras)} cameras from JSON:")
    for name, camera_config in config.cameras.items():
        print(f"  - {name}: {camera_config.type} camera ({camera_config.width}x{camera_config.height}@{camera_config.fps}fps)")
    
    print("✓ JSON camera configuration loading works!")
