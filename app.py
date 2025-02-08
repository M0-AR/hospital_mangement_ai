from flask import Flask, render_template, Response, jsonify
import cv2
import yaml
import threading
import queue
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

class CameraStream:
    def __init__(self, camera_config):
        self.name = camera_config['name']
        self.url = camera_config['url']
        self.enabled = camera_config['enabled']
        self.frame_queue = queue.Queue(maxsize=10)
        self.stopped = False
        
    def start(self):
        if self.enabled:
            threading.Thread(target=self._capture, daemon=True).start()
        return self
    
    def _capture(self):
        cap = cv2.VideoCapture(self.url)
        while not self.stopped:
            ret, frame = cap.read()
            if ret:
                if not self.frame_queue.empty():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                self.frame_queue.put(frame)
            else:
                print(f"Failed to read frame from {self.name}")
                break
        cap.release()
    
    def read(self):
        return self.frame_queue.get() if not self.frame_queue.empty() else None
    
    def stop(self):
        self.stopped = True

class AIProcessor:
    def __init__(self, ai_config):
        self.confidence_threshold = ai_config['confidence_threshold']
        # Initialize your AI model here
        # This is a placeholder for actual AI model initialization
        print("AI Model initialized")
    
    def process_frame(self, frame):
        # Placeholder for AI processing
        # Add your model inference code here
        processed_frame = frame.copy()
        cv2.putText(processed_frame, f"Processed: {datetime.now()}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return processed_frame

# Initialize cameras and AI processor
cameras = {}
for cam_config in config['cameras']:
    if cam_config['enabled']:
        cameras[cam_config['name']] = CameraStream(cam_config).start()

ai_processor = AIProcessor(config['ai_settings'])

def generate_frames(camera_name):
    while True:
        camera = cameras.get(camera_name)
        if camera:
            frame = camera.read()
            if frame is not None:
                # Process frame with AI
                processed_frame = ai_processor.process_frame(frame)
                
                # Convert to jpeg for streaming
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html', cameras=list(cameras.keys()))

@app.route('/video_feed/<camera_name>')
def video_feed(camera_name):
    if camera_name in cameras:
        return Response(generate_frames(camera_name),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    return "Camera not found", 404

@app.route('/cameras')
def get_cameras():
    return jsonify({name: {'enabled': not cam.stopped} 
                   for name, cam in cameras.items()})

if __name__ == '__main__':
    app.run(
        host=config['server']['host'],
        port=config['server']['port'],
        debug=config['server']['debug']
    )
