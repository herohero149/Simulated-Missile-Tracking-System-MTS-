"""
Trajectory Prediction Module
Linear and Kalman-based trajectory prediction
"""

import numpy as np
import time
from scipy import stats

class TrajectoryPredictor:
    def __init__(self):
        self.prediction_time = 5.0  # Predict 5 seconds ahead
        self.min_history_points = 5
        self.frame_bounds = (1280, 720)  # Default frame size
        
    def predict_trajectory(self, track):
        """Predict trajectory for a track"""
        if len(track['history']) < self.min_history_points:
            return {'status': 'insufficient_data'}
        
        # Extract position and time data
        positions = np.array([h['position'] for h in track['history']])
        timestamps = np.array([h['timestamp'] for h in track['history']])
        
        # Use both linear and Kalman predictions
        linear_pred = self._linear_prediction(positions, timestamps)
        kalman_pred = self._kalman_prediction(track)
        
        # Combine predictions (weighted average)
        combined_pred = self._combine_predictions(linear_pred, kalman_pred)
        
        return combined_pred
    
    def _linear_prediction(self, positions, timestamps):
        """Linear regression based prediction"""
        if len(positions) < 3:
            return {'status': 'insufficient_data'}
        
        # Fit linear regression for x and y coordinates
        dt = timestamps - timestamps[0]
        
        # X coordinate prediction
        slope_x, intercept_x, r_x, _, _ = stats.linregress(dt, positions[:, 0])
        # Y coordinate prediction  
        slope_y, intercept_y, r_y, _, _ = stats.linregress(dt, positions[:, 1])
        
        # Current time
        current_time = timestamps[-1] - timestamps[0]
        
        # Predict future positions
        future_times = np.arange(current_time, current_time + self.prediction_time, 0.1)
        trajectory = []
        
        for t in future_times:
            x_pred = slope_x * t + intercept_x
            y_pred = slope_y * t + intercept_y
            trajectory.append([x_pred, y_pred])
        
        trajectory = np.array(trajectory)
        
        # Calculate velocity
        velocity = [slope_x, slope_y]
        speed = np.sqrt(slope_x**2 + slope_y**2)
        
        # Find impact point (edge of frame)
        impact_point = self._calculate_impact_point(positions[-1], velocity)
        time_to_impact = self._calculate_time_to_impact(positions[-1], velocity, impact_point)
        
        return {
            'status': 'success',
            'method': 'linear',
            'trajectory': trajectory,
            'velocity': velocity,
            'speed': speed,
            'impact_point': impact_point,
            'time_to_impact': time_to_impact,
            'confidence': min(abs(r_x), abs(r_y))  # Use correlation as confidence
        }    

    def _kalman_prediction(self, track):
        """Kalman filter based prediction"""
        velocity = track['velocity']
        position = track['center']
        
        # Simple constant velocity prediction
        future_positions = []
        current_pos = np.array(position)
        vel = np.array(velocity)
        
        for t in np.arange(0, self.prediction_time, 0.1):
            future_pos = current_pos + vel * t
            future_positions.append(future_pos)
        
        trajectory = np.array(future_positions)
        speed = np.linalg.norm(velocity)
        
        # Find impact point
        impact_point = self._calculate_impact_point(position, velocity)
        time_to_impact = self._calculate_time_to_impact(position, velocity, impact_point)
        
        return {
            'status': 'success',
            'method': 'kalman',
            'trajectory': trajectory,
            'velocity': velocity,
            'speed': speed,
            'impact_point': impact_point,
            'time_to_impact': time_to_impact,
            'confidence': 0.8  # Fixed confidence for Kalman
        }
    
    def _combine_predictions(self, linear_pred, kalman_pred):
        """Combine linear and Kalman predictions"""
        if linear_pred['status'] != 'success':
            return kalman_pred
        if kalman_pred['status'] != 'success':
            return linear_pred
        
        # Weight based on confidence
        w_linear = linear_pred['confidence']
        w_kalman = kalman_pred['confidence']
        total_weight = w_linear + w_kalman
        
        if total_weight == 0:
            return kalman_pred
        
        w_linear /= total_weight
        w_kalman /= total_weight
        
        # Combine trajectories
        combined_trajectory = (w_linear * linear_pred['trajectory'] + 
                             w_kalman * kalman_pred['trajectory'])
        
        # Combine other parameters
        combined_velocity = (w_linear * np.array(linear_pred['velocity']) + 
                           w_kalman * np.array(kalman_pred['velocity']))
        
        combined_speed = np.linalg.norm(combined_velocity)
        
        # Use the prediction with higher confidence for impact point
        if w_linear > w_kalman:
            impact_point = linear_pred['impact_point']
            time_to_impact = linear_pred['time_to_impact']
        else:
            impact_point = kalman_pred['impact_point']
            time_to_impact = kalman_pred['time_to_impact']
        
        return {
            'status': 'success',
            'method': 'combined',
            'trajectory': combined_trajectory,
            'velocity': combined_velocity.tolist(),
            'speed': combined_speed,
            'impact_point': impact_point,
            'time_to_impact': time_to_impact,
            'confidence': (w_linear * linear_pred['confidence'] + 
                         w_kalman * kalman_pred['confidence'])
        }
    
    def _calculate_impact_point(self, position, velocity):
        """Calculate where trajectory intersects frame boundary"""
        x, y = position
        vx, vy = velocity
        
        if abs(vx) < 1e-6 and abs(vy) < 1e-6:
            return position  # No movement
        
        # Calculate intersection with frame boundaries
        intersections = []
        
        # Left boundary (x = 0)
        if vx < 0:
            t = -x / vx
            y_intersect = y + vy * t
            if 0 <= y_intersect <= self.frame_bounds[1]:
                intersections.append([0, y_intersect, t])
        
        # Right boundary (x = frame_width)
        if vx > 0:
            t = (self.frame_bounds[0] - x) / vx
            y_intersect = y + vy * t
            if 0 <= y_intersect <= self.frame_bounds[1]:
                intersections.append([self.frame_bounds[0], y_intersect, t])
        
        # Top boundary (y = 0)
        if vy < 0:
            t = -y / vy
            x_intersect = x + vx * t
            if 0 <= x_intersect <= self.frame_bounds[0]:
                intersections.append([x_intersect, 0, t])
        
        # Bottom boundary (y = frame_height)
        if vy > 0:
            t = (self.frame_bounds[1] - y) / vy
            x_intersect = x + vx * t
            if 0 <= x_intersect <= self.frame_bounds[0]:
                intersections.append([x_intersect, self.frame_bounds[1], t])
        
        # Return the closest intersection (smallest positive t)
        if intersections:
            intersections.sort(key=lambda x: x[2])
            for intersection in intersections:
                if intersection[2] > 0:
                    return intersection[:2]
        
        # If no intersection found, extrapolate
        t = 2.0  # 2 seconds ahead
        return [x + vx * t, y + vy * t]
    
    def _calculate_time_to_impact(self, position, velocity, impact_point):
        """Calculate time to reach impact point"""
        dx = impact_point[0] - position[0]
        dy = impact_point[1] - position[1]
        
        if abs(velocity[0]) > abs(velocity[1]):
            if abs(velocity[0]) > 1e-6:
                return dx / velocity[0]
        else:
            if abs(velocity[1]) > 1e-6:
                return dy / velocity[1]
        
        # Fallback: use distance and speed
        distance = np.sqrt(dx**2 + dy**2)
        speed = np.sqrt(velocity[0]**2 + velocity[1]**2)
        
        if speed > 1e-6:
            return distance / speed
        
        return float('inf')  # No movement