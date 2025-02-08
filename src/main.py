import cv2
import numpy as np
import threading
import queue
import time
import logging
import os
import sys
from pathlib import Path
from camera_scanner import CameraScanner
from ai_processor import AIProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('surveillance.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SurveillanceSystem:
    def __init__(self):
        self.scanner = CameraScanner()
        self.ai_processor = AIProcessor()
        self.cameras = {}
        self.frame_queues = {}
        self.prev_frames = {}
        self.running = True
        self.recording_dir = Path('recordings')
        self.recording_dir.mkdir(exist_ok=True)
        
    def start(self):
        try:
            logger.info("Starting surveillance system...")
            
            # Scan for cameras
            found_cameras = self.scanner.scan_network()
            
            if not found_cameras:
                logger.warning("No cameras found! Please check network connectivity.")
                return
            
            logger.info(f"Found {len(found_cameras)} cameras")
            
            # Setup processing for each camera
            for camera in found_cameras:
                self.frame_queues[camera['url']] = queue.Queue(maxsize=10)
                self.prev_frames[camera['url']] = None
                
                # Start camera processing thread
                thread = threading.Thread(
                    target=self.process_camera,
                    args=(camera['url'],),
                    daemon=True
                )
                thread.start()
                
                logger.info(f"Started processing for camera: {camera['url']}")
            
            # Start display thread
            display_thread = threading.Thread(target=self.display_feeds, daemon=True)
            display_thread.start()
            
            logger.info("System started successfully")
            
            # Keep main thread alive and handle user input
            while self.running:
                cmd = input("Enter command (q to quit, h for help): ").lower()
                if cmd == 'q':
                    self.running = False
                elif cmd == 'h':
                    print("""
                    Available commands:
                    q - Quit
                    h - Help
                    s - System status
                    r - Rescan for cameras
                    """)
                elif cmd == 's':
                    self.print_status()
                elif cmd == 'r':
                    self.rescan_cameras()
                    
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
        finally:
            self.cleanup()
    
    def process_camera(self, camera_url):
        """Process video feed from a single camera"""
        cap = cv2.VideoCapture(camera_url)
        logger.info(f"Started camera processing: {camera_url}")
        
        # Setup video writer for recording
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = None
        recording = False
        
        while self.running:
            try:
                ret, frame = cap.read()
                if ret:
                    # Process frame with AI
                    processed_frame, motion_detected = self.ai_processor.process_frame(
                        frame,
                        self.prev_frames[camera_url]
                    )
                    
                    self.prev_frames[camera_url] = frame.copy()
                    
                    # Handle recording if motion is detected
                    if motion_detected and not recording:
                        recording = True
                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                        video_path = self.recording_dir / f"motion_{timestamp}.avi"
                        out = cv2.VideoWriter(str(video_path), fourcc, 20.0, 
                                           (frame.shape[1], frame.shape[0]))
                        logger.info(f"Started recording: {video_path}")
                    
                    if recording:
                        out.write(processed_frame)
                        if not motion_detected:
                            recording = False
                            out.release()
                            out = None
                            logger.info("Stopped recording")
                    
                    # Update frame queue
                    if not self.frame_queues[camera_url].full():
                        self.frame_queues[camera_url].put(processed_frame)
                else:
                    logger.warning(f"Failed to read frame from {camera_url}")
                    time.sleep(1)
                    cap = cv2.VideoCapture(camera_url)
                    
            except Exception as e:
                logger.error(f"Error processing camera {camera_url}: {str(e)}")
                time.sleep(1)
                
        # Cleanup
        cap.release()
        if out is not None:
            out.release()
    
    def display_feeds(self):
        """Display all camera feeds in a grid"""
        window_name = 'Surveillance System'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        while self.running:
            try:
                frames = []
                for url, q in self.frame_queues.items():
                    if not q.empty():
                        frames.append(q.get())
                
                if frames:
                    # Calculate grid dimensions
                    n = len(frames)
                    cols = int(np.ceil(np.sqrt(n)))
                    rows = int(np.ceil(n / cols))
                    
                    # Create grid of frames
                    cell_height = 480
                    cell_width = 640
                    
                    grid = np.zeros((cell_height * rows, cell_width * cols, 3), dtype=np.uint8)
                    
                    for idx, frame in enumerate(frames):
                        i = idx // cols
                        j = idx % cols
                        
                        # Resize frame to fit cell
                        resized = cv2.resize(frame, (cell_width, cell_height))
                        
                        # Place frame in grid
                        grid[i*cell_height:(i+1)*cell_height,
                             j*cell_width:(j+1)*cell_width] = resized
                    
                    cv2.imshow(window_name, grid)
                    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    break
                    
            except Exception as e:
                logger.error(f"Error in display: {str(e)}")
                time.sleep(1)
                
        cv2.destroyAllWindows()
    
    def print_status(self):
        """Print current system status"""
        print("\nSystem Status:")
        print(f"Running: {self.running}")
        print(f"Active Cameras: {len(self.frame_queues)}")
        print(f"Recording Directory: {self.recording_dir}")
        print("\nCamera Details:")
        for url in self.frame_queues.keys():
            print(f"- {url}")
    
    def rescan_cameras(self):
        """Rescan network for new cameras"""
        logger.info("Rescanning for cameras...")
        new_cameras = self.scanner.scan_network()
        
        for camera in new_cameras:
            if camera['url'] not in self.frame_queues:
                self.frame_queues[camera['url']] = queue.Queue(maxsize=10)
                self.prev_frames[camera['url']] = None
                thread = threading.Thread(
                    target=self.process_camera,
                    args=(camera['url'],),
                    daemon=True
                )
                thread.start()
                logger.info(f"Added new camera: {camera['url']}")
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up...")
        self.running = False
        cv2.destroyAllWindows()
        logger.info("Cleanup complete")

if __name__ == "__main__":
    system = SurveillanceSystem()
    system.start()
