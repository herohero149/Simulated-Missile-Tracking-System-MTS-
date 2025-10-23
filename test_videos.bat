@echo off
echo DRDO Missile Tracking - Video Testing
echo ====================================

echo.
echo Creating test videos...
python video_test.py --create-simple --duration 20
python video_test.py --create-complex --duration 30

echo.
echo Test videos created:
echo - test_missile.mp4 (Simple scenario with 4 targets)
echo - complex_scenario.mp4 (Complex movements and patterns)

echo.
echo Choose an option:
echo 1. Test simple video
echo 2. Test complex video  
echo 3. Test both videos
echo 4. Exit

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo Testing simple video...
    python run.py --source test_missile.mp4 --save-video --output-dir video_results
)
if "%choice%"=="2" (
    echo Testing complex video...
    python run.py --source complex_scenario.mp4 --save-video --output-dir video_results
)
if "%choice%"=="3" (
    echo Testing simple video...
    python run.py --source test_missile.mp4 --save-video --output-dir video_results
    echo.
    echo Testing complex video...
    python run.py --source complex_scenario.mp4 --save-video --output-dir video_results
)
if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
)

echo.
echo Video analysis complete!
echo Check the video_results folder for output files.
pause