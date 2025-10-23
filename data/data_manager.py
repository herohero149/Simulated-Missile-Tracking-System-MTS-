"""
Data Management Module
Handles CSV and SQLite data storage with auto-save functionality
"""

import pandas as pd
import sqlite3
import os
import time
from datetime import datetime
import json

class DataManager:
    def __init__(self, csv_file='tracking_data.csv', db_file='tracking_data.db'):
        self.csv_file = csv_file
        self.db_file = db_file
        self.data_buffer = []
        
        # Initialize database
        self._init_database()
        
        # Initialize CSV with headers if not exists
        self._init_csv()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                object_id INTEGER,
                position_x REAL,
                position_y REAL,
                velocity_x REAL,
                velocity_y REAL,
                speed REAL,
                confidence REAL,
                bbox_x1 REAL,
                bbox_y1 REAL,
                bbox_x2 REAL,
                bbox_y2 REAL,
                age INTEGER,
                hits INTEGER,
                prediction_method TEXT,
                impact_point_x REAL,
                impact_point_y REAL,
                time_to_impact REAL,
                prediction_confidence REAL
            )
        ''')
        
        # Create session table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time REAL,
                end_time REAL,
                total_objects INTEGER,
                total_predictions INTEGER,
                success_rate REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_csv(self):
        """Initialize CSV file with headers"""
        if not os.path.exists(self.csv_file):
            headers = [
                'timestamp', 'object_id', 'position_x', 'position_y',
                'velocity_x', 'velocity_y', 'speed', 'confidence',
                'bbox_x1', 'bbox_y1', 'bbox_x2', 'bbox_y2',
                'age', 'hits', 'prediction_method',
                'impact_point_x', 'impact_point_y', 'time_to_impact',
                'prediction_confidence'
            ]
            
            df = pd.DataFrame(columns=headers)
            df.to_csv(self.csv_file, index=False)
    
    def save_data(self, tracked_objects, predictions):
        """Save tracking data to both CSV and SQLite"""
        if not tracked_objects:
            return
        
        current_time = time.time()
        rows = []
        
        for obj_id, track in tracked_objects.items():
            # Get prediction data if available
            pred = predictions.get(obj_id, {})
            
            # Extract track data
            center = track.get('center', [0, 0])
            velocity = track.get('velocity', [0, 0])
            bbox = track.get('bbox', [0, 0, 0, 0])
            
            # Extract prediction data
            impact_point = pred.get('impact_point', [0, 0])
            
            row = {
                'timestamp': current_time,
                'object_id': obj_id,
                'position_x': center[0],
                'position_y': center[1],
                'velocity_x': velocity[0],
                'velocity_y': velocity[1],
                'speed': pred.get('speed', 0),
                'confidence': track.get('confidence', 0),
                'bbox_x1': bbox[0],
                'bbox_y1': bbox[1],
                'bbox_x2': bbox[2],
                'bbox_y2': bbox[3],
                'age': track.get('age', 0),
                'hits': track.get('hits', 0),
                'prediction_method': pred.get('method', 'none'),
                'impact_point_x': impact_point[0],
                'impact_point_y': impact_point[1],
                'time_to_impact': pred.get('time_to_impact', 0),
                'prediction_confidence': pred.get('confidence', 0)
            }
            
            rows.append(row)
        
        if rows:
            # Save to CSV
            self._save_to_csv(rows)
            
            # Save to SQLite
            self._save_to_sqlite(rows)
            
            print(f"Saved {len(rows)} tracking records")
    
    def _save_to_csv(self, rows):
        """Save data to CSV file"""
        try:
            df = pd.DataFrame(rows)
            df.to_csv(self.csv_file, mode='a', header=False, index=False)
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def _save_to_sqlite(self, rows):
        """Save data to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_file)
            
            for row in rows:
                conn.execute('''
                    INSERT INTO tracking_data (
                        timestamp, object_id, position_x, position_y,
                        velocity_x, velocity_y, speed, confidence,
                        bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                        age, hits, prediction_method,
                        impact_point_x, impact_point_y, time_to_impact,
                        prediction_confidence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['timestamp'], row['object_id'], row['position_x'], row['position_y'],
                    row['velocity_x'], row['velocity_y'], row['speed'], row['confidence'],
                    row['bbox_x1'], row['bbox_y1'], row['bbox_x2'], row['bbox_y2'],
                    row['age'], row['hits'], row['prediction_method'],
                    row['impact_point_x'], row['impact_point_y'], row['time_to_impact'],
                    row['prediction_confidence']
                ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving to SQLite: {e}")
    
    def get_statistics(self):
        """Get tracking statistics from database"""
        try:
            conn = sqlite3.connect(self.db_file)
            
            # Total objects tracked
            cursor = conn.execute('SELECT COUNT(DISTINCT object_id) FROM tracking_data')
            total_objects = cursor.fetchone()[0]
            
            # Total predictions made
            cursor = conn.execute('SELECT COUNT(*) FROM tracking_data WHERE prediction_method != "none"')
            total_predictions = cursor.fetchone()[0]
            
            # Average confidence
            cursor = conn.execute('SELECT AVG(prediction_confidence) FROM tracking_data WHERE prediction_confidence > 0')
            avg_confidence = cursor.fetchone()[0] or 0
            
            # Success rate (predictions with confidence > 0.7)
            cursor = conn.execute('SELECT COUNT(*) FROM tracking_data WHERE prediction_confidence > 0.7')
            successful_predictions = cursor.fetchone()[0]
            
            success_rate = (successful_predictions / max(1, total_predictions)) * 100
            
            conn.close()
            
            return {
                'total_objects': total_objects,
                'total_predictions': total_predictions,
                'average_confidence': avg_confidence,
                'success_rate': success_rate
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def export_data(self, format='json', filename=None):
        """Export data in specified format"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tracking_export_{timestamp}.{format}'
        
        try:
            if format == 'json':
                conn = sqlite3.connect(self.db_file)
                df = pd.read_sql_query('SELECT * FROM tracking_data', conn)
                conn.close()
                
                df.to_json(filename, orient='records', indent=2)
            elif format == 'csv':
                # CSV already exists, just copy it
                import shutil
                shutil.copy2(self.csv_file, filename)
            
            print(f"Data exported to {filename}")
            return filename
        except Exception as e:
            print(f"Error exporting data: {e}")
            return None
    
    def close(self):
        """Close data manager and perform final save"""
        # Get final statistics
        stats = self.get_statistics()
        print(f"Session Statistics:")
        print(f"  Total Objects Tracked: {stats.get('total_objects', 0)}")
        print(f"  Total Predictions: {stats.get('total_predictions', 0)}")
        print(f"  Average Confidence: {stats.get('average_confidence', 0):.3f}")
        print(f"  Success Rate: {stats.get('success_rate', 0):.1f}%")
        
        # Export final data
        self.export_data('json')
        print(f"Data saved to {self.csv_file} and {self.db_file}")