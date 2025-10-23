# Simulated Missile Tracking System

A real-time missile/drone tracking simulator using computer vision and machine learning for trajectory prediction.

## Features

- **Object Detection**: YOLOv8 with MobileNet SSD fallback
- **Multi-Object Tracking**: SORT-based tracking with Kalman filtering
- **Trajectory Prediction**: Linear regression and Kalman-based prediction
- **Dual Terminal UI**: 
  - LOCKING terminal: Object IDs and lock status
  - TRAJECTORY terminal: Velocity, predicted impact, time-to-impact, success ratio
- **Auto-save**: Data saved every 5 seconds to CSV and SQLite
- **Video Output**: Optional annotated video recording

## Installation

1. Install Python 3.8+ and pip
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python main.py
```

### With Video File
```bash
python main.py --source path/to/video.mp4
```

### Command Line Options
- `--source`: Video source (0 for webcam, path for video file)
- `--save-video`: Enable video output recording
- `--confidence`: Detection confidence threshold (default: 0.5)

## System Architecture

### Detection Module (`tracking/detector.py`)
- Primary: YOLOv8 nano model for real-time detection
- Fallback: MobileNet SSD or background subtraction
- Configurable confidence and NMS thresholds

### Tracking Module (`tracking/tracker.py`)
- SORT-like multi-object tracking
- Kalman filter for state estimation
- Hungarian algorithm for data association
- Track lifecycle management

### Prediction Module (`tracking/predictor.py`)
- Linear regression trajectory prediction
- Kalman-based velocity prediction
- Combined prediction with confidence weighting
- Impact point calculation and time-to-impact estimation

### UI Module (`ui/terminal_ui.py`)
- Real-time dual terminal display
- Color-coded threat levels
- Live statistics and system status

### Data Management (`data/data_manager.py`)
- Auto-save to CSV and SQLite every 5 seconds
- Session statistics tracking
- Data export capabilities

## Output Files

- `tracking_data.csv`: Real-time tracking data
- `tracking_data.db`: SQLite database with full tracking history
- `output.avi`: Annotated video output (if enabled)
- `tracking_export_YYYYMMDD_HHMMSS.json`: Session export

## Terminal Interface

### LOCKING Terminal
```
ID    STATUS      CONFIDENCE   AGE     HITS    POSITION
1     LOCKED      0.892        45      23      (640, 360)
2     TRACKING    0.734        12      8       (320, 180)
3     ACQUIRING   0.543        3       2       (960, 540)
```

### TRAJECTORY Terminal
```
ID    VELOCITY        SPEED     IMPACT POINT    TTI     CONF
1     (12.3,-8.7)     15.1      (1280,120)      8.2s    0.892
2     (-5.2,15.6)     16.4      (0,720)         12.1s   0.734
3     (0.8,-2.1)      2.2       (980,0)         45.3s   0.543
```

## Performance

- **Detection**: 20-30 FPS on modern hardware
- **Tracking**: Handles 10+ simultaneous objects
- **Prediction**: Sub-millisecond trajectory calculation
- **Memory**: ~200MB typical usage

## Legal Notice

This is a simulation system for educational and research purposes. It is designed for legal defense applications and complies with applicable regulations.

## Troubleshooting

### Common Issues

1. **Camera not detected**: Check camera permissions and connections
2. **Low FPS**: Reduce resolution or use YOLOv8n model
3. **Poor tracking**: Adjust confidence thresholds
4. **Missing dependencies**: Run `pip install -r requirements.txt`

### Performance Optimization

- Use GPU acceleration: Install `torch` with CUDA support
- Reduce frame resolution for better performance
- Adjust detection confidence threshold
- Use video file input for consistent testing

## Development

### Project Structure
```
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── tracking/              # Core tracking modules
│   ├── detector.py        # Object detection
│   ├── tracker.py         # Multi-object tracking
│   └── predictor.py       # Trajectory prediction
├── ui/                    # User interface
│   └── terminal_ui.py     # Dual terminal display
└── data/                  # Data management
    └── data_manager.py    # CSV/SQLite storage
```

### Adding New Features

1. **Custom Detection Models**: Modify `detector.py`
2. **Advanced Tracking**: Extend `tracker.py` 
3. **New Prediction Methods**: Add to `predictor.py`
4. **UI Enhancements**: Update `terminal_ui.py`

## License

Educational and research use only. See LICENSE file for details.