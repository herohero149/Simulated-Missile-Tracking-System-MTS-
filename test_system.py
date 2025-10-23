#!/usr/bin/env python3
"""
Test script for Missile Tracking System
Tests individual components without camera
"""

import numpy as np
import time
from tracking.detector import ObjectDetector
from tracking.tracker import ObjectTracker
from tracking.predictor import TrajectoryPredictor
from ui.terminal_ui import TerminalUI
from data.data_manager import DataManager

def create_mock_detection(x, y, w=50, h=50, confidence=0.8):
    """Create a mock detection for testing"""
    return {
        'bbox': [x, y, x+w, y+h],
        'confidence': confidence,
        'class_id': 0,
        'center': [x + w/2, y + h/2]
    }

def test_components():
    """Test all system components"""
    print("Testing Missile Tracking System Components")
    print("=" * 50)
    
    # Test detector initialization
    print("1. Testing Detector...")
    try:
        detector = ObjectDetector()
        print(f"   ✓ Detector initialized: {detector.model_type}")
    except Exception as e:
        print(f"   ✗ Detector failed: {e}")
        return False
    
    # Test tracker
    print("2. Testing Tracker...")
    try:
        tracker = ObjectTracker()
        
        # Create mock detections
        detections = [
            create_mock_detection(100, 100),
            create_mock_detection(200, 150),
        ]
        
        tracked = tracker.update(detections)
        print(f"   ✓ Tracker working: {len(tracked)} objects tracked")
    except Exception as e:
        print(f"   ✗ Tracker failed: {e}")
        return False
    
    # Test predictor
    print("3. Testing Predictor...")
    try:
        predictor = TrajectoryPredictor()
        
        # Create mock track with history
        mock_track = {
            'center': [150, 125],
            'velocity': [5, -2],
            'history': [
                {'position': [140, 130], 'timestamp': time.time() - 0.5},
                {'position': [145, 128], 'timestamp': time.time() - 0.3},
                {'position': [150, 125], 'timestamp': time.time()}
            ]
        }
        
        prediction = predictor.predict_trajectory(mock_track)
        print(f"   ✓ Predictor working: {prediction.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ✗ Predictor failed: {e}")
        return False
    
    # Test data manager
    print("4. Testing Data Manager...")
    try:
        data_manager = DataManager(csv_file='test_data.csv', db_file='test_data.db')
        
        # Test save
        mock_objects = {1: mock_track}
        mock_predictions = {1: prediction}
        data_manager.save_data(mock_objects, mock_predictions)
        
        stats = data_manager.get_statistics()
        print(f"   ✓ Data Manager working: {stats}")
        data_manager.close()
    except Exception as e:
        print(f"   ✗ Data Manager failed: {e}")
        return False
    
    # Test UI (brief test)
    print("5. Testing UI...")
    try:
        ui = TerminalUI()
        ui.update_data(tracked, {1: prediction})
        print("   ✓ UI initialized successfully")
    except Exception as e:
        print(f"   ✗ UI failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All components tested successfully!")
    print("System is ready to run.")
    print("\nTo start the system:")
    print("  python main.py              # Use webcam")
    print("  python run.py --help        # See all options")
    
    return True

if __name__ == "__main__":
    success = test_components()
    if not success:
        print("\n⚠ Some components failed. Check dependencies:")
        print("  pip install -r requirements.txt")
        exit(1)