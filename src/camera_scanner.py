import cv2
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraScanner:
    def __init__(self):
        self.found_cameras = []
        self.common_credentials = [
            ('admin', 'admin'),
            ('admin', '12345'),
            ('admin', 'password'),
            ('', '')  # No credentials
        ]
        
    def test_camera_url(self, ip, port):
        for username, password in self.common_credentials:
            urls = [
                f"rtsp://{ip}:{port}/",
                f"rtsp://{username}:{password}@{ip}:{port}/",
                f"rtsp://{ip}:{port}/stream1",
                f"http://{ip}:{port}/video",
                f"rtsp://{username}:{password}@{ip}:{port}/stream1",
                f"rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor"
            ]
            
            for url in urls:
                try:
                    logger.info(f"Testing camera URL: {url}")
                    cap = cv2.VideoCapture(url)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            self.found_cameras.append({
                                'url': url,
                                'ip': ip,
                                'port': port,
                                'status': 'active',
                                'resolution': (int(cap.get(3)), int(cap.get(4)))
                            })
                            cap.release()
                            logger.info(f"Found working camera at {url}")
                            return True
                    cap.release()
                except Exception as e:
                    logger.debug(f"Failed to connect to {url}: {str(e)}")
                    continue
        return False

    def scan_network(self, ip_ranges=None):
        """
        Scan network for cameras. If no IP ranges provided, try common local networks.
        """
        if ip_ranges is None:
            ip_ranges = ['192.168.1', '192.168.0', '10.0.0', '172.16.0']
            
        common_ports = [554, 8000, 8080, 80, 8554, 9000]
        logger.info("Starting network scan for cameras...")
        
        for ip_range in ip_ranges:
            logger.info(f"Scanning IP range: {ip_range}.0/24")
            with ThreadPoolExecutor(max_workers=50) as executor:
                for i in range(1, 255):
                    ip = f"{ip_range}.{i}"
                    for port in common_ports:
                        executor.submit(self.test_camera_url, ip, port)
        
        logger.info(f"Scan complete. Found {len(self.found_cameras)} cameras")
        return self.found_cameras

    def get_camera_info(self):
        """Return detailed information about found cameras"""
        return [{
            'url': cam['url'],
            'ip': cam['ip'],
            'port': cam['port'],
            'status': cam['status'],
            'resolution': cam.get('resolution', 'Unknown')
        } for cam in self.found_cameras]
