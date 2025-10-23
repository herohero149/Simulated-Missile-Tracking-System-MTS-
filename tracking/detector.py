"""
Object Detection Module
Supports YOLOv8 with MobileNet SSD fallback
"""

import cv2
import numpy as np
import os
from ultralytics import YOLO
import torch

class ObjectDetector:
    def __init__(self):
        self.model = None
        self.model_type = None
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4
        
        # Initialize detection model
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize YOLO or fallback to MobileNet SSD"""
        try:
            # Try YOLOv8 first
            self.model = YOLO('yolov8n.pt')  # nano version for speed
            self.model_type = 'yolo'
            print("Initialized YOLOv8 detector")
        except Exception as e:
            print(f"YOLOv8 failed: {e}")
            try:
                # Fallback to MobileNet SSD
                self._initialize_mobilenet()
                self.model_type = 'mobilenet'
                print("Initialized MobileNet SSD detector")
            except Exception as e2:
                print(f"MobileNet SSD failed: {e2}")
                raise RuntimeError("Failed to initialize any detection model")
    
    def _initialize_mobilenet(self):
        """Initialize MobileNet SSD as fallback"""
        # Download MobileNet SSD if not present
        config_path = 'models/MobileNetSSD_deploy.prototxt'
        weights_path = 'models/MobileNetSSD_deploy.caffemodel'
        
        if not os.path.exists('models'):
            os.makedirs('models')
            
        # For demo purposes, we'll use a simple background subtractor
        # In production, you'd download the actual MobileNet SSD files
        self.model = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        
    def detect(self, frame):
        """Detect objects in frame"""
        if self.model_type == 'yolo':
            return self._detect_yolo(frame)
        else:
            return self._detect_mobilenet(frame)
    
    def _detect_yolo(self, frame):
        """YOLO detection"""
        results = self.model(frame, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    if confidence > self.confidence_threshold:
                        detections.append({
                            'bbox': [x1, y1, x2, y2],
                            'confidence': confidence,
                            'class_id': class_id,
                            'center': [(x1 + x2) / 2, (y1 + y2) / 2]
                        })
        
        return detections
    
    def _detect_mobilenet(self, frame):
        """MobileNet SSD / Background subtraction detection"""
        # Apply background subtraction
        fg_mask = self.model.apply(frame)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio and size
                aspect_ratio = w / h
                if 0.2 < aspect_ratio < 5.0 and w > 20 and h > 20:
                    detections.append({
                        'bbox': [x, y, x + w, y + h],
                        'confidence': 0.8,  # Fixed confidence for background subtraction
                        'class_id': 0,  # Generic object class
                        'center': [x + w/2, y + h/2]
                    })
        
        return detections
    
    def get_model_info(self):
        """Get information about current model"""
        return {
            'type': self.model_type,
            'confidence_threshold': self.confidence_threshold,
            'nms_threshold': self.nms_threshold
        }