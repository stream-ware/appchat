"""
Camera Manager for RTSP/ONVIF integration
Real camera feeds and motion detection
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None

logger = logging.getLogger("streamware.cameras")


@dataclass
class CameraFeed:
    """Camera feed configuration"""
    id: str
    name: str
    url: str
    type: str = "rtsp"
    status: str = "offline"
    location: str = ""
    resolution: str = ""
    fps: int = 0
    last_frame: Optional[str] = None
    motion_detected: bool = False
    recording: bool = False
    created_at: str = ""
    updated_at: str = ""


class CameraManager:
    """Camera management system with RTSP/ONVIF support"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.cameras_dir = self.data_dir / "cameras"
        self.cameras_dir.mkdir(parents=True, exist_ok=True)
        
        self.cameras: Dict[str, CameraFeed] = {}
        self.load_cameras()
        
        # Check OpenCV availability
        self.opencv_available = self._check_opencv()
        
        logger.info(f"✅ Camera Manager initialized - {len(self.cameras)} cameras loaded")
    
    def _check_opencv(self) -> bool:
        """Check if OpenCV is available"""
        if CV2_AVAILABLE:
            logger.info("✅ OpenCV available for camera processing")
            return True
        else:
            logger.warning("⚠️ OpenCV not available - install with: pip install opencv-python")
            return False
    
    def load_cameras(self):
        """Load camera configurations"""
        cameras_file = self.cameras_dir / "cameras.json"
        if cameras_file.exists():
            try:
                data = json.loads(cameras_file.read_text(encoding='utf-8'))
                for cam_data in data.get('cameras', []):
                    camera = CameraFeed(**cam_data)
                    self.cameras[camera.id] = camera
                logger.info(f"📁 Loaded {len(self.cameras)} cameras")
            except Exception as e:
                logger.error(f"Error loading cameras: {e}")
    
    def save_cameras(self):
        """Save camera configurations"""
        cameras_file = self.cameras_dir / "cameras.json"
        data = {
            "cameras": [asdict(cam) for cam in self.cameras.values()],
            "updated_at": datetime.now().isoformat()
        }
        cameras_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
    
    def add_camera(self, name: str, url: str, location: str = "", camera_type: str = "rtsp") -> str:
        """Add new camera"""
        camera_id = f"cam_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        camera = CameraFeed(
            id=camera_id,
            name=name,
            url=url,
            type=camera_type,
            location=location,
            status="offline",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.cameras[camera_id] = camera
        self.save_cameras()
        
        logger.info(f"📷 Added camera: {name} ({camera_id})")
        return camera_id
    
    def remove_camera(self, camera_id: str) -> bool:
        """Remove camera"""
        if camera_id in self.cameras:
            del self.cameras[camera_id]
            self.save_cameras()
            logger.info(f"🗑️ Removed camera: {camera_id}")
            return True
        return False
    
    def get_camera(self, camera_id: str) -> Optional[CameraFeed]:
        """Get camera by ID"""
        return self.cameras.get(camera_id)
    
    def get_all_cameras(self) -> List[CameraFeed]:
        """Get all cameras"""
        return list(self.cameras.values())
    
    def update_camera_status(self, camera_id: str, status: str):
        """Update camera status"""
        if camera_id in self.cameras:
            self.cameras[camera_id].status = status
            self.cameras[camera_id].updated_at = datetime.now().isoformat()
            self.save_cameras()
    
    async def test_camera_connection(self, camera_id: str) -> bool:
        """Test camera connection"""
        if not self.opencv_available:
            self.update_camera_status(camera_id, "error")
            return False
        
        camera = self.get_camera(camera_id)
        if not camera:
            return False
        
        try:
            # Try to connect to camera
            cap = cv2.VideoCapture(camera.url)
            
            if cap.isOpened():
                # Try to read a frame
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    self.update_camera_status(camera_id, "online")
                    logger.info(f"✅ Camera {camera_id} is online")
                    return True
                else:
                    self.update_camera_status(camera_id, "error")
                    logger.warning(f"⚠️ Camera {camera_id} connected but no frame")
                    return False
            else:
                self.update_camera_status(camera_id, "offline")
                logger.warning(f"❌ Camera {camera_id} is offline")
                return False
                
        except Exception as e:
            self.update_camera_status(camera_id, "error")
            logger.error(f"❌ Error testing camera {camera_id}: {e}")
            return False
    
    async def get_camera_frame(self, camera_id: str) -> Optional[Any]:
        """Get current frame from camera"""
        if not self.opencv_available:
            return None
        
        camera = self.get_camera(camera_id)
        if not camera or camera.status != "online":
            return None
        
        try:
            cap = cv2.VideoCapture(camera.url)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    # Save frame info
                    camera.last_frame = datetime.now().isoformat()
                    camera.updated_at = datetime.now().isoformat()
                    
                    # Basic motion detection
                    if self.detect_motion(frame):
                        camera.motion_detected = True
                    else:
                        camera.motion_detected = False
                    
                    return frame
            
        except Exception as e:
            logger.error(f"Error getting frame from {camera_id}: {e}")
            self.update_camera_status(camera_id, "error")
        
        return None
    
    def detect_motion(self, frame: Any) -> bool:
        """Simple motion detection"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # For demo, just check if there's any variation in the frame
            # In real implementation, you'd compare with previous frame
            std_dev = cv2.meanStdDev(gray)[1]
            
            # If standard deviation is high, there's motion
            return std_dev > 10
            
        except Exception:
            return False
    
    def get_camera_stats(self) -> Dict:
        """Get camera statistics"""
        total = len(self.cameras)
        online = sum(1 for cam in self.cameras.values() if cam.status == "online")
        offline = sum(1 for cam in self.cameras.values() if cam.status == "offline")
        error = sum(1 for cam in self.cameras.values() if cam.status == "error")
        motion = sum(1 for cam in self.cameras.values() if cam.motion_detected)
        
        return {
            "total": total,
            "online": online,
            "offline": offline,
            "error": error,
            "motion_detected": motion,
            "opencv_available": self.opencv_available
        }
    
    def create_sample_cameras(self):
        """Create sample RTSP cameras for testing"""
        sample_cameras = [
            {
                "name": "Kamera wejścia",
                "url": "rtsp://admin:password@192.168.1.100:554/stream1",
                "location": "Wejście główne"
            },
            {
                "name": "Kamera parkingu",
                "url": "rtsp://admin:password@192.168.1.101:554/stream1",
                "location": "Parking"
            },
            {
                "name": "Kamera biura",
                "url": "rtsp://admin:password@192.168.1.102:554/stream1",
                "location": "Open space"
            }
        ]
        
        for cam_data in sample_cameras:
            self.add_camera(
                name=cam_data["name"],
                url=cam_data["url"],
                location=cam_data["location"]
            )
        
        logger.info(f"📷 Created {len(sample_cameras)} sample cameras")


# Singleton
camera_manager = CameraManager()


def get_cameras_list() -> List[Dict]:
    """Get all cameras as dict list"""
    return [asdict(cam) for cam in camera_manager.get_all_cameras()]


def get_camera_details(camera_id: str) -> Optional[Dict]:
    """Get camera details"""
    camera = camera_manager.get_camera(camera_id)
    return asdict(camera) if camera else None


def add_camera(name: str, url: str, location: str = "") -> str:
    """Add new camera"""
    return camera_manager.add_camera(name, url, location)


def remove_camera(camera_id: str) -> bool:
    """Remove camera"""
    return camera_manager.remove_camera(camera_id)


def get_camera_stats() -> Dict:
    """Get camera statistics"""
    return camera_manager.get_camera_stats()


def create_sample_cameras():
    """Create sample cameras for testing"""
    camera_manager.create_sample_cameras()
