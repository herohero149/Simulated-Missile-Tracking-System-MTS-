"""
Object Tracking Module
Implements SORT-like tracking algorithm
"""

import numpy as np
from scipy.optimize import linear_sum_assignment
from collections import defaultdict
import time

class KalmanFilter:
    """Simple Kalman filter for object tracking"""
    def __init__(self, initial_state):
        # State: [x, y, vx, vy]
        self.state = np.array(initial_state, dtype=float)
        self.covariance = np.eye(4) * 1000
        
        # State transition matrix (constant velocity model)
        self.F = np.array([[1, 0, 1, 0],
                          [0, 1, 0, 1],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]], dtype=float)
        
        # Measurement matrix
        self.H = np.array([[1, 0, 0, 0],
                          [0, 1, 0, 0]], dtype=float)
        
        # Process noise
        self.Q = np.eye(4) * 0.1
        
        # Measurement noise
        self.R = np.eye(2) * 1
        
    def predict(self):
        """Predict next state"""
        self.state = self.F @ self.state
        self.covariance = self.F @ self.covariance @ self.F.T + self.Q
        return self.state[:2]  # Return position
    
    def update(self, measurement):
        """Update with measurement"""
        y = measurement - self.H @ self.state
        S = self.H @ self.covariance @ self.H.T + self.R
        K = self.covariance @ self.H.T @ np.linalg.inv(S)
        
        self.state = self.state + K @ y
        self.covariance = (np.eye(4) - K @ self.H) @ self.covariance

class Track:
    """Individual track object"""
    def __init__(self, detection, track_id):
        self.id = track_id
        self.kalman = KalmanFilter([detection['center'][0], detection['center'][1], 0, 0])
        self.age = 0
        self.hits = 1
        self.hit_streak = 1
        self.time_since_update = 0
        self.history = []
        self.bbox = detection['bbox']
        self.confidence = detection['confidence']
        self.last_update = time.time()
        
    def predict(self):
        """Predict next position"""
        predicted_pos = self.kalman.predict()
        self.age += 1
        self.time_since_update += 1
        return predicted_pos
    
    def update(self, detection):
        """Update track with detection"""
        self.kalman.update(np.array(detection['center']))
        self.hits += 1
        self.hit_streak += 1
        self.time_since_update = 0
        self.bbox = detection['bbox']
        self.confidence = detection['confidence']
        self.last_update = time.time()
        
        # Store history for trajectory prediction
        self.history.append({
            'position': detection['center'],
            'timestamp': time.time(),
            'bbox': detection['bbox']
        })
        
        # Keep only recent history (last 30 frames)
        if len(self.history) > 30:
            self.history.pop(0)
    
    def get_state(self):
        """Get current track state"""
        return {
            'id': self.id,
            'bbox': self.bbox,
            'center': [self.kalman.state[0], self.kalman.state[1]],
            'velocity': [self.kalman.state[2], self.kalman.state[3]],
            'confidence': self.confidence,
            'age': self.age,
            'hits': self.hits,
            'history': self.history,
            'last_update': self.last_update
        }

class ObjectTracker:
    """SORT-like multi-object tracker"""
    def __init__(self):
        self.tracks = []
        self.next_id = 1
        self.max_age = 30  # Maximum frames to keep track without detection
        self.min_hits = 3   # Minimum hits before track is confirmed
        self.iou_threshold = 0.3
        
    def update(self, detections):
        """Update tracker with new detections"""
        # Predict all tracks
        predicted_tracks = []
        for track in self.tracks:
            predicted_pos = track.predict()
            predicted_tracks.append((track, predicted_pos))
        
        # Associate detections with tracks
        matched_tracks, unmatched_detections, unmatched_tracks = self._associate_detections_to_tracks(
            detections, predicted_tracks)
        
        # Update matched tracks
        for track_idx, det_idx in matched_tracks:
            self.tracks[track_idx].update(detections[det_idx])
        
        # Create new tracks for unmatched detections
        for det_idx in unmatched_detections:
            new_track = Track(detections[det_idx], self.next_id)
            self.tracks.append(new_track)
            self.next_id += 1
        
        # Remove old tracks
        self.tracks = [track for track in self.tracks 
                      if track.time_since_update < self.max_age]
        
        # Return confirmed tracks
        confirmed_tracks = {}
        for track in self.tracks:
            if track.hits >= self.min_hits:
                confirmed_tracks[track.id] = track.get_state()
        
        return confirmed_tracks
    
    def _associate_detections_to_tracks(self, detections, predicted_tracks):
        """Associate detections with existing tracks using IoU"""
        if len(predicted_tracks) == 0:
            return [], list(range(len(detections))), []
        
        if len(detections) == 0:
            return [], [], list(range(len(predicted_tracks)))
        
        # Compute IoU matrix
        iou_matrix = np.zeros((len(predicted_tracks), len(detections)))
        
        for t, (track, pred_pos) in enumerate(predicted_tracks):
            for d, detection in enumerate(detections):
                iou_matrix[t, d] = self._calculate_iou(track.bbox, detection['bbox'])
        
        # Use Hungarian algorithm for optimal assignment
        if min(iou_matrix.shape) > 0:
            matched_indices = linear_sum_assignment(-iou_matrix)  # Negative for maximization
            matched_tracks = []
            
            for t, d in zip(matched_indices[0], matched_indices[1]):
                if iou_matrix[t, d] > self.iou_threshold:
                    matched_tracks.append((t, d))
            
            unmatched_detections = [d for d in range(len(detections)) 
                                  if d not in matched_indices[1]]
            unmatched_tracks = [t for t in range(len(predicted_tracks)) 
                              if t not in matched_indices[0]]
        else:
            matched_tracks = []
            unmatched_detections = list(range(len(detections)))
            unmatched_tracks = list(range(len(predicted_tracks)))
        
        return matched_tracks, unmatched_detections, unmatched_tracks
    
    def _calculate_iou(self, bbox1, bbox2):
        """Calculate Intersection over Union (IoU)"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def get_track_count(self):
        """Get number of active tracks"""
        return len([track for track in self.tracks if track.hits >= self.min_hits])