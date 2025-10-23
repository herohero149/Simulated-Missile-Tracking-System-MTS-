#!/usr/bin/env python3
"""
Simulated Missile Tracking System
Real-time object tracking with trajectory prediction
"""

import cv2
import numpy as np
import threading
import time
import os
from datetime import datetime
from tracking.detector import ObjectDetector
from tracking.tracker import ObjectTracker
from tracking.predictor import TrajectoryPredictor
from ui.terminal_ui import TerminalUI
from data.data_manager import DataManager

class MissileTrackingSystem:
    def __init__(self):
        self.detector = ObjectDetector()
        self.tracker = ObjectTracker()
        self.predictor = TrajectoryPredictor()
        self.ui = TerminalUI()
        self.data_manager = DataManager()
        
        self.running = False
        self.frame_count = 0
        self.fps = 0
        self.last_save_time = time.time()
        self.is_video_file = False
        self.current_frame = 0
        self.total_frames = 0
        self.video_fps = 30
        self.video_duration = 0
        
    def initialize_camera(self, source=0):
        """Initialize camera or video source"""
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera/video source")
        
        # Get source info
        if isinstance(source, str):
            # Video file
            self.is_video_file = True
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.video_duration = self.total_frames / self.video_fps if self.video_fps > 0 else 0
            print(f"Video file: {source}")
            print(f"Duration: {self.video_duration:.1f}s, FPS: {self.video_fps:.1f}, Frames: {self.total_frames}")
        else:
            # Camera
            self.is_video_file = False
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            print(f"Camera source: {source}")
        
    def process_frame(self, frame):
        """Process single frame for detection and tracking"""
        # Detect objects
        detections = self.detector.detect(frame)
        
        # Update tracker
        tracked_objects = self.tracker.update(detections)
        
        # Predict trajectories
        predictions = {}
        for obj_id, track in tracked_objects.items():
            prediction = self.predictor.predict_trajectory(track)
            predictions[obj_id] = prediction
            
        return tracked_objects, predictions
    
    def run(self, source=0, save_video=False):
        """Main execution loop"""
        self.initialize_camera(source)
        self.running = True
        
        # Setup video writer if needed
        video_writer = None
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter('output.avi', fourcc, 20.0, (1280, 720))
        
        # Start UI in separate thread
        ui_thread = threading.Thread(target=self.ui.run, daemon=True)
        ui_thread.start()
        
        start_time = time.time()
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    if self.is_video_file:
                        print("End of video file reached")
                    break
                
                self.current_frame += 1
                
                # Process frame
                tracked_objects, predictions = self.process_frame(frame)
                
                # Update UI data
                self.ui.update_data(tracked_objects, predictions)
                
                # Draw annotations on frame
                annotated_frame = self.draw_annotations(frame, tracked_objects, predictions)
                
                # Save video frame if enabled
                if video_writer:
                    video_writer.write(annotated_frame)
                
                # Display frame
                cv2.imshow('Missile Tracking System', annotated_frame)
                
                # Video playback control
                if self.is_video_file:
                    # Maintain video FPS for playback
                    delay = int(1000 / self.video_fps) if self.video_fps > 0 else 33
                    key = cv2.waitKey(delay) & 0xFF
                    
                    # Video controls
                    if key == ord(' '):  # Spacebar to pause
                        cv2.waitKey(0)
                    elif key == ord('s'):  # 's' to step frame
                        pass
                    elif key == ord('q'):  # 'q' to quit
                        break
                else:
                    # Real-time camera
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # Auto-save data every 5 seconds
                current_time = time.time()
                if current_time - self.last_save_time >= 5.0:
                    self.data_manager.save_data(tracked_objects, predictions)
                    self.last_save_time = current_time
                
                # Calculate FPS
                self.frame_count += 1
                if self.frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    self.fps = self.frame_count / elapsed
                

                    
        except KeyboardInterrupt:
            print("\nShutdown requested...")
        finally:
            self.cleanup(video_writer)
    
    def draw_annotations(self, frame, tracked_objects, predictions):
        """Draw tracking annotations on frame"""
        annotated = frame.copy()
        
        for obj_id, track in tracked_objects.items():
            # Draw bounding box
            x1, y1, x2, y2 = track['bbox']
            cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # Draw object ID
            cv2.putText(annotated, f'ID: {obj_id}', (int(x1), int(y1)-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw trajectory if available
            if obj_id in predictions and 'trajectory' in predictions[obj_id]:
                trajectory = predictions[obj_id]['trajectory']
                for i in range(len(trajectory)-1):
                    pt1 = (int(trajectory[i][0]), int(trajectory[i][1]))
                    pt2 = (int(trajectory[i+1][0]), int(trajectory[i+1][1]))
                    cv2.line(annotated, pt1, pt2, (255, 0, 0), 2)
                
                # Draw predicted impact point
                if 'impact_point' in predictions[obj_id]:
                    impact = predictions[obj_id]['impact_point']
                    cv2.circle(annotated, (int(impact[0]), int(impact[1])), 10, (0, 0, 255), -1)
                    cv2.putText(annotated, 'IMPACT', (int(impact[0])-30, int(impact[1])-15),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Draw system info
        cv2.putText(annotated, f'FPS: {self.fps:.1f}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(annotated, f'Objects: {len(tracked_objects)}', (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Video progress info
        if self.is_video_file:
            progress = (self.current_frame / max(1, self.total_frames)) * 100
            time_elapsed = self.current_frame / max(1, self.video_fps)
            cv2.putText(annotated, f'Progress: {progress:.1f}% ({time_elapsed:.1f}s/{self.video_duration:.1f}s)', 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(annotated, 'Controls: SPACE=Pause, S=Step, Q=Quit', (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        cv2.putText(annotated, 'Missile Tracking System', (10, annotated.shape[0]-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return annotated
    
    def cleanup(self, video_writer=None):
        """Cleanup resources"""
        self.running = False
        if hasattr(self, 'cap'):
            self.cap.release()
        if video_writer:
            video_writer.release()
        cv2.destroyAllWindows()
        
        # Final data save
        print("Saving final data...")
        self.data_manager.close()

if __name__ == "__main__":
    system = MissileTrackingSystem()
    
    print("Simulated Missile Tracking System")
    print("=====================================")
    print("Press 'q' to quit")
    print("Starting system...")
    
    try:
        system.run(source=0, save_video=True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("System shutdown complete.")