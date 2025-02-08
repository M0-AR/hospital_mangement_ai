import cv2
import numpy as np
from pathlib import Path
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self, models_dir='models'):
        self.models_dir = Path(models_dir)
        self.models_loaded = False
        self.load_models()
        
    def load_models(self):
        """Load pre-downloaded AI models"""
        try:
            # Load face detection model
            face_cascade_path = self.models_dir / 'haarcascade_frontalface_default.xml'
            if not face_cascade_path.exists():
                # If model doesn't exist, use OpenCV's built-in cascades
                face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            
            self.face_cascade = cv2.CascadeClassifier(str(face_cascade_path))
            
            # Load person detection model (HOG descriptor)
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            
            self.models_loaded = True
            logger.info("AI models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            self.models_loaded = False
    
    def detect_faces(self, frame):
        """Detect faces in the frame"""
        if not self.models_loaded:
            return frame
            
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, 'Face', (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        except Exception as e:
            logger.error(f"Error in face detection: {str(e)}")
            
        return frame
    
    def detect_motion(self, frame, prev_frame):
        """Detect motion between frames"""
        if prev_frame is None:
            return frame, False
            
        try:
            # Convert frames to grayscale
            gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate difference
            diff = cv2.absdiff(gray1, gray2)
            blur = cv2.GaussianBlur(diff, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_detected = False
            for contour in contours:
                if cv2.contourArea(contour) > 1000:
                    motion_detected = True
                    (x, y, w, h) = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, 'Motion', (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            return frame, motion_detected
            
        except Exception as e:
            logger.error(f"Error in motion detection: {str(e)}")
            return frame, False
    
    def detect_people(self, frame):
        """Detect people in the frame using HOG descriptor"""
        if not self.models_loaded:
            return frame
            
        try:
            # Detect people
            boxes, weights = self.hog.detectMultiScale(frame, winStride=(8,8))
            
            # Draw boxes around detected people
            for (x, y, w, h) in boxes:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(frame, 'Person', (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        except Exception as e:
            logger.error(f"Error in person detection: {str(e)}")
            
        return frame
    
    def process_frame(self, frame, prev_frame=None, detect_faces=True, detect_motion=True, detect_people=True):
        """Process a frame with all available detections"""
        if frame is None:
            return None, False
            
        processed_frame = frame.copy()
        motion_detected = False
        
        try:
            if detect_faces:
                processed_frame = self.detect_faces(processed_frame)
            
            if detect_motion and prev_frame is not None:
                processed_frame, motion_detected = self.detect_motion(processed_frame, prev_frame)
            
            if detect_people:
                processed_frame = self.detect_people(processed_frame)
            
            # Add timestamp
            cv2.putText(processed_frame, f"Time: {cv2.getTickCount() / cv2.getTickFrequency():.2f}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
        except Exception as e:
            logger.error(f"Error in frame processing: {str(e)}")
            return frame, False
            
        return processed_frame, motion_detected
