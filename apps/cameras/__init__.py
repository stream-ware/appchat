"""
Cameras App - RTSP/ONVIF monitoring and motion detection
"""

from .camera_manager import CameraManager, get_cameras_list, get_camera_details, add_camera, remove_camera, get_camera_stats, create_sample_cameras

__all__ = ["CameraManager", "get_cameras_list", "get_camera_details", "add_camera", "remove_camera", "get_camera_stats", "create_sample_cameras"]
