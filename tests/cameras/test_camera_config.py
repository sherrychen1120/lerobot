#!/usr/bin/env python3
"""
Test script to verify camera configuration loading from JSON file.
"""

import sys
import os

# Add the lerobot path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "third_party", "lerobot", "src"))

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

if __name__ == "__main__":
    test_json_camera_config()
