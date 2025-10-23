#!/usr/bin/env python3
"""
Video Analysis Tool for Missile Tracking System
Provides detailed analysis and statistics for video tracking results
"""

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import os
import argparse
import numpy as np
from datetime import datetime

class VideoAnalyzer:
    def __init__(self, data_file="tracking_data.db"):
        self.data_file = data_file
        self.df = None
        
    def load_data(self):
        """Load tracking data from database"""
        if not os.path.exists(self.data_file):
            print(f"Error: Data file not found: {self.data_file}")
            return False
        
        try:
            conn = sqlite3.connect(self.data_file)
            self.df = pd.read_sql_query("SELECT * FROM tracking_data", conn)
            conn.close()
            
            if len(self.df) == 0:
                print("No tracking data found in database")
                return False
            
            print(f"Loaded {len(self.df)} tracking records")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def generate_statistics(self):
        """Generate comprehensive tracking statistics"""
        if self.df is None:
            return None
        
        stats = {}
        
        # Basic statistics
        stats['total_records'] = len(self.df)
        stats['unique_objects'] = self.df['object_id'].nunique()
        stats['duration'] = self.df['timestamp'].max() - self.df['timestamp'].min()
        
        # Detection statistics
        stats['avg_confidence'] = self.df['confidence'].mean()
        stats['min_confidence'] = self.df['confidence'].min()
        stats['max_confidence'] = self.df['confidence'].max()
        
        # Tracking quality
        stats['avg_track_length'] = self.df.groupby('object_id').size().mean()
        stats['longest_track'] = self.df.groupby('object_id').size().max()
        stats['shortest_track'] = self.df.groupby('object_id').size().min()
        
        # Speed analysis
        stats['avg_speed'] = self.df['speed'].mean()
        stats['max_speed'] = self.df['speed'].max()
        stats['min_speed'] = self.df['speed'].min()
        
        # Prediction statistics
        prediction_data = self.df[self.df['prediction_method'] != 'none']
        if len(prediction_data) > 0:
            stats['prediction_success_rate'] = (prediction_data['prediction_confidence'] > 0.7).mean() * 100
            stats['avg_prediction_confidence'] = prediction_data['prediction_confidence'].mean()
            stats['avg_time_to_impact'] = prediction_data['time_to_impact'].mean()
        else:
            stats['prediction_success_rate'] = 0
            stats['avg_prediction_confidence'] = 0
            stats['avg_time_to_impact'] = 0
        
        return stats
    
    def plot_trajectories(self, output_file="trajectories.png"):
        """Plot object trajectories"""
        if self.df is None:
            return False
        
        plt.figure(figsize=(12, 8))
        
        # Plot each object's trajectory
        for obj_id in self.df['object_id'].unique():
            obj_data = self.df[self.df['object_id'] == obj_id].sort_values('timestamp')
            plt.plot(obj_data['position_x'], obj_data['position_y'], 
                    marker='o', markersize=2, label=f'Object {obj_id}', alpha=0.7)
            
            # Mark start and end points
            if len(obj_data) > 0:
                start = obj_data.iloc[0]
                end = obj_data.iloc[-1]
                plt.scatter(start['position_x'], start['position_y'], 
                           color='green', s=100, marker='s', alpha=0.8)
                plt.scatter(end['position_x'], end['position_y'], 
                           color='red', s=100, marker='X', alpha=0.8)
        
        plt.xlabel('X Position (pixels)')
        plt.ylabel('Y Position (pixels)')
        plt.title('Object Trajectories\n(Green squares = Start, Red X = End)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.gca().invert_yaxis()  # Invert Y axis to match image coordinates
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Trajectory plot saved: {output_file}")
        return True
    
    def plot_speed_analysis(self, output_file="speed_analysis.png"):
        """Plot speed analysis over time"""
        if self.df is None:
            return False
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Speed over time for each object
        for obj_id in self.df['object_id'].unique():
            obj_data = self.df[self.df['object_id'] == obj_id].sort_values('timestamp')
            time_relative = obj_data['timestamp'] - obj_data['timestamp'].min()
            ax1.plot(time_relative, obj_data['speed'], 
                    marker='o', markersize=3, label=f'Object {obj_id}', alpha=0.7)
        
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Speed (pixels/frame)')
        ax1.set_title('Speed Over Time by Object')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Speed distribution histogram
        ax2.hist(self.df['speed'], bins=30, alpha=0.7, edgecolor='black')
        ax2.axvline(self.df['speed'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {self.df["speed"].mean():.1f}')
        ax2.axvline(self.df['speed'].median(), color='orange', linestyle='--', 
                   label=f'Median: {self.df["speed"].median():.1f}')
        ax2.set_xlabel('Speed (pixels/frame)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Speed Distribution')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Speed analysis plot saved: {output_file}")
        return True
    
    def plot_confidence_analysis(self, output_file="confidence_analysis.png"):
        """Plot confidence analysis"""
        if self.df is None:
            return False
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Confidence over time
        time_relative = self.df['timestamp'] - self.df['timestamp'].min()
        scatter = ax1.scatter(time_relative, self.df['confidence'], 
                             c=self.df['object_id'], alpha=0.6, cmap='tab10')
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Detection Confidence')
        ax1.set_title('Detection Confidence Over Time')
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax1, label='Object ID')
        
        # Confidence vs Speed
        ax2.scatter(self.df['speed'], self.df['confidence'], 
                   c=self.df['object_id'], alpha=0.6, cmap='tab10')
        ax2.set_xlabel('Speed (pixels/frame)')
        ax2.set_ylabel('Detection Confidence')
        ax2.set_title('Confidence vs Speed')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Confidence analysis plot saved: {output_file}")
        return True
    
    def generate_report(self, output_file="analysis_report.txt"):
        """Generate comprehensive text report"""
        stats = self.generate_statistics()
        if stats is None:
            return False
        
        report = []
        report.append("DRDO MISSILE TRACKING SYSTEM - VIDEO ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Data source: {self.data_file}")
        report.append("")
        
        report.append("BASIC STATISTICS")
        report.append("-" * 20)
        report.append(f"Total tracking records: {stats['total_records']:,}")
        report.append(f"Unique objects tracked: {stats['unique_objects']}")
        report.append(f"Total duration: {stats['duration']:.1f} seconds")
        report.append(f"Average records per object: {stats['total_records']/stats['unique_objects']:.1f}")
        report.append("")
        
        report.append("DETECTION QUALITY")
        report.append("-" * 20)
        report.append(f"Average confidence: {stats['avg_confidence']:.3f}")
        report.append(f"Confidence range: {stats['min_confidence']:.3f} - {stats['max_confidence']:.3f}")
        report.append(f"High confidence rate (>0.8): {(self.df['confidence'] > 0.8).mean()*100:.1f}%")
        report.append("")
        
        report.append("TRACKING PERFORMANCE")
        report.append("-" * 20)
        report.append(f"Average track length: {stats['avg_track_length']:.1f} frames")
        report.append(f"Longest track: {stats['longest_track']} frames")
        report.append(f"Shortest track: {stats['shortest_track']} frames")
        report.append("")
        
        report.append("SPEED ANALYSIS")
        report.append("-" * 20)
        report.append(f"Average speed: {stats['avg_speed']:.1f} pixels/frame")
        report.append(f"Speed range: {stats['min_speed']:.1f} - {stats['max_speed']:.1f} pixels/frame")
        report.append(f"High speed objects (>15 px/frame): {(self.df['speed'] > 15).sum()} records")
        report.append("")
        
        report.append("PREDICTION PERFORMANCE")
        report.append("-" * 20)
        report.append(f"Prediction success rate: {stats['prediction_success_rate']:.1f}%")
        report.append(f"Average prediction confidence: {stats['avg_prediction_confidence']:.3f}")
        report.append(f"Average time to impact: {stats['avg_time_to_impact']:.1f} seconds")
        report.append("")
        
        # Object-specific analysis
        report.append("OBJECT-SPECIFIC ANALYSIS")
        report.append("-" * 20)
        for obj_id in sorted(self.df['object_id'].unique()):
            obj_data = self.df[self.df['object_id'] == obj_id]
            report.append(f"Object {obj_id}:")
            report.append(f"  Records: {len(obj_data)}")
            report.append(f"  Avg confidence: {obj_data['confidence'].mean():.3f}")
            report.append(f"  Avg speed: {obj_data['speed'].mean():.1f} px/frame")
            report.append(f"  Duration: {obj_data['timestamp'].max() - obj_data['timestamp'].min():.1f}s")
        
        # Write report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Analysis report saved: {output_file}")
        return True
    
    def full_analysis(self, output_dir="analysis_results"):
        """Run complete analysis and generate all outputs"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print("Running comprehensive video analysis...")
        
        # Generate all plots and reports
        self.plot_trajectories(os.path.join(output_dir, "trajectories.png"))
        self.plot_speed_analysis(os.path.join(output_dir, "speed_analysis.png"))
        self.plot_confidence_analysis(os.path.join(output_dir, "confidence_analysis.png"))
        self.generate_report(os.path.join(output_dir, "analysis_report.txt"))
        
        # Export data to CSV for further analysis
        csv_file = os.path.join(output_dir, "tracking_data_export.csv")
        self.df.to_csv(csv_file, index=False)
        print(f"Data exported to CSV: {csv_file}")
        
        print(f"\nAnalysis complete! Results saved in: {output_dir}")
        print("Files generated:")
        print("- trajectories.png: Object movement paths")
        print("- speed_analysis.png: Speed patterns over time")
        print("- confidence_analysis.png: Detection confidence analysis")
        print("- analysis_report.txt: Comprehensive text report")
        print("- tracking_data_export.csv: Raw data export")

def main():
    parser = argparse.ArgumentParser(description='Video Analysis for DRDO Tracking System')
    parser.add_argument('--data', type=str, default='tracking_data.db', 
                       help='Path to tracking database file')
    parser.add_argument('--output', type=str, default='analysis_results',
                       help='Output directory for analysis results')
    
    args = parser.parse_args()
    
    analyzer = VideoAnalyzer(args.data)
    
    if analyzer.load_data():
        analyzer.full_analysis(args.output)
    else:
        print("Failed to load tracking data. Make sure to run video tracking first.")

if __name__ == "__main__":
    main()