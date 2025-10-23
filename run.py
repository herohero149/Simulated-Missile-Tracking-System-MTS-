#!/usr/bin/env python3
"""
Missile Tracking System - Launcher Script
Handles command line arguments and system initialization
"""

import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='Simulated Missile Tracking System')
    parser.add_argument('--source', type=str, default='0', 
                       help='Video source (0 for webcam, path for video file)')
    parser.add_argument('--save-video', action='store_true',
                       help='Save annotated video output')
    parser.add_argument('--confidence', type=float, default=0.5,
                       help='Detection confidence threshold (0.0-1.0)')
    parser.add_argument('--output-dir', type=str, default='.',
                       help='Output directory for saved files')
    
    args = parser.parse_args()
    
    # Convert source to int if it's a number
    try:
        source = int(args.source)
    except ValueError:
        source = args.source
    
    # Create output directory
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Change to output directory
    os.chdir(args.output_dir)
    
    # Import and run main system
    try:
        from main import MissileTrackingSystem
        
        system = MissileTrackingSystem()
        
        # Set confidence threshold
        system.detector.confidence_threshold = args.confidence
        
        print("Simulated Missile Tracking System")
        print("=====================================")
        print(f"Source: {source}")
        print(f"Confidence: {args.confidence}")
        print(f"Save Video: {args.save_video}")
        print(f"Output Directory: {args.output_dir}")
        print("Press 'q' in video window to quit")
        print("Starting system...")
        
        system.run(source=source, save_video=args.save_video)
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()