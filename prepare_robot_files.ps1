# PowerShell script to prepare files for upload to robot
# File name: prepare_robot_files.ps1

Write-Host "=== Preparing WAVEGO Robot Files ===" -ForegroundColor Green
Write-Host ""

$SourceDir = "c:\Users\devil\Documents\GitHub\WAVEGO-main\robo\RPi"
$OutputDir = "c:\Users\devil\Documents\GitHub\WAVEGO-main\robo\robot_update"

Write-Host "Source directory: $SourceDir" -ForegroundColor Yellow
Write-Host "Output directory: $OutputDir" -ForegroundColor Yellow
Write-Host ""

# Create output directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "Created output directory: $OutputDir" -ForegroundColor Green
}

# List of files to copy
$FilesToCopy = @(
    "robot.py",
    "camera_opencv.py", 
    "webServer.py",
    "app.py",
    "BollshiiOs.py",
    "simple_speed_test.py"
)

Write-Host "Copying updated files to robot_update directory..." -ForegroundColor Green

foreach ($File in $FilesToCopy) {
    $SourceFile = Join-Path $SourceDir $File
    $DestFile = Join-Path $OutputDir $File
    
    if (Test-Path $SourceFile) {
        Copy-Item $SourceFile $DestFile -Force
        Write-Host "✓ Copied: $File" -ForegroundColor Green
    } else {
        Write-Host "✗ Missing: $File" -ForegroundColor Red
    }
}

# Create upload instructions
$InstructionsFile = Join-Path $OutputDir "UPLOAD_INSTRUCTIONS.txt"
$Instructions = "=== Robot Update Instructions ===

1. Copy all files from this directory to the robot at: /home/devil/WAVEGO/RPi/

2. On the robot, run these commands:

   # Stop the service
   sudo systemctl stop wavego.service
   
   # Backup original files (optional)
   sudo cp /home/devil/WAVEGO/RPi/robot.py /home/devil/WAVEGO/RPi/robot.py.backup
   sudo cp /home/devil/WAVEGO/RPi/camera_opencv.py /home/devil/WAVEGO/RPi/camera_opencv.py.backup
   sudo cp /home/devil/WAVEGO/RPi/webServer.py /home/devil/WAVEGO/RPi/webServer.py.backup
   sudo cp /home/devil/WAVEGO/RPi/app.py /home/devil/WAVEGO/RPi/app.py.backup
   
   # Set correct permissions
   sudo chown devil:devil /home/devil/WAVEGO/RPi/*.py
   sudo chmod +x /home/devil/WAVEGO/RPi/*.py
   
   # Test the speed functionality
   cd /home/devil/WAVEGO/RPi/
   python3 simple_speed_test.py
   
   # Start the service
   sudo systemctl start wavego.service
   
   # Check service status
   sudo systemctl status wavego.service
   
   # View logs
   journalctl -u wavego.service -f

3. Test the web interface:
   - Open browser to robot IP
   - Test speed slider in Move Control section
   - Test BolliOs button in Actions section

4. API endpoints for testing:
   - Speed status: curl http://localhost:5000/api/speed/status
   - Set speed: curl http://localhost:5000/api/speed/set/75

=== Files Updated ===
- robot.py: Added integrated SpeedManager, fixed speed functions
- camera_opencv.py: Improved speed command parsing and BolliOs integration  
- webServer.py: Added speed debugging logs and BolliOs commands
- app.py: Added speed status API endpoints
- BollshiiOs.py: Gyro balance system with green LED indication
- simple_speed_test.py: Test script for speed functionality

=== Features Added ===
Speed Control: Web slider now controls robot movement speed
BolliOs Button: Gyro balance system with green LED when active
Debug Tools: Comprehensive logging for troubleshooting
API Endpoints: RESTful speed control and status
Error Handling: Robust error recovery and validation

If you encounter issues, check the service logs:
journalctl -u wavego.service -n 50 --no-pager"

Set-Content -Path $InstructionsFile -Value $Instructions -Encoding UTF8

Write-Host ""
Write-Host "✓ Created upload instructions: UPLOAD_INSTRUCTIONS.txt" -ForegroundColor Green
Write-Host ""
Write-Host "=== Files Ready for Robot Update ===" -ForegroundColor Green
Write-Host "Output directory: $OutputDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy all files from $OutputDir to the robot" -ForegroundColor White
Write-Host "2. Follow instructions in UPLOAD_INSTRUCTIONS.txt" -ForegroundColor White
Write-Host "3. Test speed slider and BolliOs button" -ForegroundColor White
Write-Host ""