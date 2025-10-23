"""
Dual Terminal UI Module
LOCKING terminal: Object IDs and lock status
TRAJECTORY terminal: Velocity, predicted impact, time-to-impact, success ratio
"""

import threading
import time
import os
import sys
from datetime import datetime

class TerminalUI:
    def __init__(self):
        self.tracked_objects = {}
        self.predictions = {}
        self.running = False
        self.lock = threading.Lock()
        self.success_count = 0
        self.total_predictions = 0
        
    def update_data(self, tracked_objects, predictions):
        """Update UI data thread-safely"""
        with self.lock:
            self.tracked_objects = tracked_objects.copy()
            self.predictions = predictions.copy()
            
            # Update success statistics
            for obj_id, pred in predictions.items():
                if pred.get('status') == 'success':
                    self.total_predictions += 1
                    if pred.get('confidence', 0) > 0.7:
                        self.success_count += 1
    
    def run(self):
        """Run dual terminal display"""
        self.running = True
        
        # Clear screen and setup
        self._clear_screen()
        
        while self.running:
            try:
                self._display_terminals()
                time.sleep(0.5)  # Update every 500ms
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"UI Error: {e}")
                time.sleep(1)
    
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _display_terminals(self):
        """Display both terminal views"""
        with self.lock:
            # Move cursor to top
            print("\033[H", end="")
            
            # Header
            print("=" * 80)
            print("DRDO SIMULATED MISSILE TRACKING SYSTEM".center(80))
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(80))
            print("=" * 80)
            
            # Split screen layout
            self._display_locking_terminal()
            print("-" * 80)
            self._display_trajectory_terminal()
            print("=" * 80)
            
            # System status
            success_rate = (self.success_count / max(1, self.total_predictions)) * 100
            print(f"System Status: ACTIVE | Objects: {len(self.tracked_objects)} | Success Rate: {success_rate:.1f}%")
            print("Press Ctrl+C to exit")
    
    def _display_locking_terminal(self):
        """Display LOCKING terminal - Object IDs and lock status"""
        print("LOCKING TERMINAL".center(80))
        print("-" * 80)
        
        if not self.tracked_objects:
            print("NO TARGETS DETECTED".center(80))
            print()
            return
        
        # Header
        print(f"{'ID':<5} {'STATUS':<12} {'CONFIDENCE':<12} {'AGE':<8} {'HITS':<8} {'POSITION':<20}")
        print("-" * 80)
        
        for obj_id, track in self.tracked_objects.items():
            # Determine lock status
            confidence = track.get('confidence', 0)
            age = track.get('age', 0)
            hits = track.get('hits', 0)
            
            if confidence > 0.8 and hits > 5:
                status = "LOCKED"
                status_color = "\033[92m"  # Green
            elif confidence > 0.6:
                status = "TRACKING"
                status_color = "\033[93m"  # Yellow
            else:
                status = "ACQUIRING"
                status_color = "\033[91m"  # Red
            
            # Position
            center = track.get('center', [0, 0])
            position = f"({center[0]:.0f}, {center[1]:.0f})"
            
            # Display row
            print(f"{status_color}{obj_id:<5} {status:<12} {confidence:<12.3f} {age:<8} {hits:<8} {position:<20}\033[0m")
        
        print()
    
    def _display_trajectory_terminal(self):
        """Display TRAJECTORY terminal - Velocity, impact, time-to-impact"""
        print("TRAJECTORY TERMINAL".center(80))
        print("-" * 80)
        
        if not self.predictions:
            print("NO TRAJECTORY DATA".center(80))
            print()
            return
        
        # Header
        print(f"{'ID':<5} {'VELOCITY':<15} {'SPEED':<10} {'IMPACT POINT':<15} {'TTI':<8} {'CONF':<8}")
        print("-" * 80)
        
        for obj_id, pred in self.predictions.items():
            if pred.get('status') != 'success':
                continue
            
            # Velocity
            velocity = pred.get('velocity', [0, 0])
            vel_str = f"({velocity[0]:.1f},{velocity[1]:.1f})"
            
            # Speed
            speed = pred.get('speed', 0)
            
            # Impact point
            impact = pred.get('impact_point', [0, 0])
            impact_str = f"({impact[0]:.0f},{impact[1]:.0f})"
            
            # Time to impact
            tti = pred.get('time_to_impact', float('inf'))
            if tti == float('inf'):
                tti_str = "∞"
            else:
                tti_str = f"{tti:.1f}s"
            
            # Confidence
            confidence = pred.get('confidence', 0)
            
            # Color coding based on threat level
            if tti < 3.0 and tti != float('inf'):
                color = "\033[91m"  # Red - High threat
            elif tti < 10.0:
                color = "\033[93m"  # Yellow - Medium threat
            else:
                color = "\033[92m"  # Green - Low threat
            
            print(f"{color}{obj_id:<5} {vel_str:<15} {speed:<10.1f} {impact_str:<15} {tti_str:<8} {confidence:<8.3f}\033[0m")
        
        print()
    
    def stop(self):
        """Stop the UI"""
        self.running = False