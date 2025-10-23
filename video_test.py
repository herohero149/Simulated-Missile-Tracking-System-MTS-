#!/usr/bin/env python3
"""
Video Testing Script for Missile Tracking System
Creates test videos and runs tracking analysis
"""

import cv2
import numpy as np
import os
import argparse
from datetime import datetime

def create_test_video(filename="test_missile.mp4", duration=30, fps=30):
    """Create a test video with moving objects simulating missiles/drones"""
    
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    total_frames = duration * fps
    
    # Define multiple moving objects
    objects = [
        {
            'start_pos': (50, 100),
            'velocity': (8, 3),
            'size': (40, 20),
            'color': (0, 0, 255),  # Red
            'start_frame': 0
        },
        {
            'start_pos': (1200, 200),
            'velocity': (-12, 5),
            'size': (35, 25),
            'color': (255, 0, 0),  # Blue
            'start_frame': 60
        },
        {
            'start_pos': (640, 50),
            'velocity': (2, 15),
            'size': (30, 30),
            'color': (0, 255, 0),  # Green
            'start_frame': 120
        },
        {
            'start_pos': (100, 600),
            'velocity': (15, -8),
            'size': (45, 15),
            'color': (255, 255, 0),  # Cyan
            'start_frame': 180
        }
    ]
    
    print(f"Creating test video: {filename}")
    print(f"Duration: {duration}s, FPS: {fps}, Total frames: {total_frames}")
    
    for frame_num in range(total_frames):
        # Create background (sky-like gradient)
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create gradient background
        for y in range(height):
            intensity = int(135 + (120 * y / height))  # Sky blue gradient
            frame[y, :] = [intensity, intensity//2, 50]
        
        # Add some clouds (static)
        cv2.ellipse(frame, (200, 150), (80, 40), 0, 0, 360, (255, 255, 255), -1)
        cv2.ellipse(frame, (800, 100), (120, 60), 0, 0, 360, (255, 255, 255), -1)
        cv2.ellipse(frame, (1000, 250), (90, 45), 0, 0, 360, (255, 255, 255), -1)
        
        # Draw moving objects
        for obj in objects:
            if frame_num >= obj['start_frame']:
                # Calculate current position
                frames_active = frame_num - obj['start_frame']
                current_x = obj['start_pos'][0] + obj['velocity'][0] * frames_active
                current_y = obj['start_pos'][1] + obj['velocity'][1] * frames_active
                
                # Check if object is still in frame
                if (0 <= current_x <= width and 0 <= current_y <= height):
                    # Draw object (ellipse to simulate missile/drone)
                    center = (int(current_x), int(current_y))
                    axes = obj['size']
                    
                    # Draw main body
                    cv2.ellipse(frame, center, axes, 0, 0, 360, obj['color'], -1)
                    
                    # Add trail effect
                    for i in range(1, 6):
                        trail_x = current_x - obj['velocity'][0] * i * 2
                        trail_y = current_y - obj['velocity'][1] * i * 2
                        if 0 <= trail_x <= width and 0 <= trail_y <= height:
                            trail_center = (int(trail_x), int(trail_y))
                            trail_size = (max(5, axes[0] - i*3), max(3, axes[1] - i*2))
                            alpha = 1.0 - (i * 0.15)
                            trail_color = tuple(int(c * alpha) for c in obj['color'])
                            cv2.ellipse(frame, trail_center, trail_size, 0, 0, 360, trail_color, -1)
        
        # Add frame info
        cv2.putText(frame, f"Frame: {frame_num}/{total_frames}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {frame_num/fps:.1f}s", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "DRDO Test Video - Simulated Targets", (10, height-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        out.write(frame)
        
        # Progress indicator
        if frame_num % (fps * 2) == 0:  # Every 2 seconds
            progress = (frame_num / total_frames) * 100
            print(f"Progress: {progress:.1f}%")
    
    out.release()
    print(f"✓ Test video created: {filename}")
    return filename

def create_complex_scenario(filename="complex_scenario.mp4", duration=45):
    """Create a more complex scenario with crossing paths and varying speeds"""
    
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, 30, (width, height))
    
    total_frames = duration * 30
    
    # More complex objects with changing velocities
    objects = [
        # Fast crossing missile
        {'start_pos': (0, 360), 'velocity': (25, -5), 'size': (50, 15), 'color': (0, 0, 255), 'start_frame': 30},
        # Slow drone with zigzag
        {'start_pos': (200, 100), 'velocity': (3, 8), 'size': (25, 25), 'color': (255, 0, 0), 'start_frame': 0, 'zigzag': True},
        # Accelerating target
        {'start_pos': (1200, 500), 'velocity': (-8, -12), 'size': (35, 20), 'color': (0, 255, 0), 'start_frame': 90, 'accel': True},
        # Circular motion
        {'start_pos': (640, 360), 'velocity': (0, 0), 'size': (30, 30), 'color': (255, 255, 0), 'start_frame': 150, 'circular': True},
        # Erratic movement
        {'start_pos': (100, 200), 'velocity': (10, 5), 'size': (40, 25), 'color': (255, 0, 255), 'start_frame': 200, 'erratic': True}
    ]
    
    print(f"Creating complex scenario: {filename}")
    
    for frame_num in range(total_frames):
        # Create background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Gradient background
        for y in range(height):
            intensity = int(120 + (100 * y / height))
            frame[y, :] = [intensity, intensity//3, 30]
        
        # Add terrain features
        cv2.rectangle(frame, (0, height-100), (width, height), (34, 139, 34), -1)  # Ground
        
        # Draw objects with complex behaviors
        for obj in objects:
            if frame_num >= obj['start_frame']:
                frames_active = frame_num - obj['start_frame']
                
                # Calculate position based on movement type
                if obj.get('zigzag'):
                    # Zigzag pattern
                    base_x = obj['start_pos'][0] + obj['velocity'][0] * frames_active
                    base_y = obj['start_pos'][1] + obj['velocity'][1] * frames_active
                    zigzag_offset = 30 * np.sin(frames_active * 0.2)
                    current_x = base_x + zigzag_offset
                    current_y = base_y
                elif obj.get('accel'):
                    # Accelerating movement
                    accel_factor = 1 + (frames_active * 0.01)
                    current_x = obj['start_pos'][0] + obj['velocity'][0] * frames_active * accel_factor
                    current_y = obj['start_pos'][1] + obj['velocity'][1] * frames_active * accel_factor
                elif obj.get('circular'):
                    # Circular motion
                    radius = 150
                    angle = frames_active * 0.05
                    current_x = obj['start_pos'][0] + radius * np.cos(angle)
                    current_y = obj['start_pos'][1] + radius * np.sin(angle)
                elif obj.get('erratic'):
                    # Erratic movement with random changes
                    base_x = obj['start_pos'][0] + obj['velocity'][0] * frames_active
                    base_y = obj['start_pos'][1] + obj['velocity'][1] * frames_active
                    noise_x = 20 * np.sin(frames_active * 0.3) * np.cos(frames_active * 0.1)
                    noise_y = 15 * np.cos(frames_active * 0.25) * np.sin(frames_active * 0.15)
                    current_x = base_x + noise_x
                    current_y = base_y + noise_y
                else:
                    # Linear movement
                    current_x = obj['start_pos'][0] + obj['velocity'][0] * frames_active
                    current_y = obj['start_pos'][1] + obj['velocity'][1] * frames_active
                
                # Draw if in bounds
                if (0 <= current_x <= width and 0 <= current_y <= height):
                    center = (int(current_x), int(current_y))
                    cv2.ellipse(frame, center, obj['size'], 0, 0, 360, obj['color'], -1)
                    
                    # Add ID label
                    cv2.putText(frame, f"T{objects.index(obj)+1}", 
                               (int(current_x)-10, int(current_y)-20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add scenario info
        cv2.putText(frame, f"Complex Scenario - Frame: {frame_num}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Multiple Target Types: Linear, Zigzag, Accelerating, Circular, Erratic", 
                   (10, height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        out.write(frame)
    
    out.release()
    print(f"✓ Complex scenario created: {filename}")
    return filename

def run_video_analysis(video_path, output_dir="video_results"):
    """Run tracking analysis on a video file"""
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return False
    
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get video info
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    cap.release()
    
    print(f"\nAnalyzing video: {video_path}")
    print(f"Duration: {duration:.1f}s, FPS: {fps}, Frames: {frame_count}")
    
    # Run tracking system
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_video = os.path.join(output_dir, f"tracked_{timestamp}.avi")
    
    command = f"python run.py --source \"{video_path}\" --save-video --output-dir \"{output_dir}\""
    print(f"Running: {command}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Video Testing for DRDO Missile Tracking')
    parser.add_argument('--create-simple', action='store_true', help='Create simple test video')
    parser.add_argument('--create-complex', action='store_true', help='Create complex scenario video')
    parser.add_argument('--analyze', type=str, help='Analyze existing video file')
    parser.add_argument('--duration', type=int, default=30, help='Video duration in seconds')
    parser.add_argument('--all', action='store_true', help='Create both test videos and analyze them')
    
    args = parser.parse_args()
    
    if args.all or args.create_simple:
        video1 = create_test_video("test_missile.mp4", args.duration)
        if args.all:
            run_video_analysis(video1)
    
    if args.all or args.create_complex:
        video2 = create_complex_scenario("complex_scenario.mp4", args.duration + 15)
        if args.all:
            run_video_analysis(video2)
    
    if args.analyze:
        run_video_analysis(args.analyze)
    
    if not any([args.create_simple, args.create_complex, args.analyze, args.all]):
        print("DRDO Video Testing Tool")
        print("======================")
        print("Usage examples:")
        print("  python video_test.py --create-simple     # Create simple test video")
        print("  python video_test.py --create-complex    # Create complex scenario")
        print("  python video_test.py --analyze video.mp4 # Analyze existing video")
        print("  python video_test.py --all               # Create and analyze both")
        print("\nThis will create test videos with simulated missiles/drones for tracking.")

if __name__ == "__main__":
    main()