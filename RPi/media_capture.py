#!/usr/bin/env python
"""
Photo and Video Capture Module for WAVEGO Robot

Features:
- Photo capture from video stream
- Video recording functionality
- Automatic file naming with timestamps
- Quality settings and formats
- Storage management
"""

import cv2
import os
import time
import datetime
import threading
import json
from pathlib import Path

class MediaCapture:
    def __init__(self, base_path=None):
        """
        Initialize Media Capture
        
        Args:
            base_path (str): Base directory for saving media files
        """
        # Set up paths
        if base_path is None:
            self.base_path = os.path.join(os.path.dirname(__file__), 'media')
        else:
            self.base_path = base_path
            
        self.photos_path = os.path.join(self.base_path, 'photos')
        self.videos_path = os.path.join(self.base_path, 'videos')
        
        # Create directories if they don't exist
        os.makedirs(self.photos_path, exist_ok=True)
        os.makedirs(self.videos_path, exist_ok=True)
        
        # Video recording state
        self.is_recording = False
        self.video_writer = None
        self.recording_thread = None
        self.current_recording_path = None
        
        # Settings
        self.photo_quality = 95  # JPEG quality (0-100)
        self.video_fps = 20
        self.video_codec = 'XVID'  # or 'MJPG'
        self.video_format = '.avi'
        self.photo_format = '.jpg'
        
        # Statistics
        self.photos_taken = 0
        self.videos_recorded = 0
        self.total_recording_time = 0
        
        print(f"Media Capture initialized - Photos: {self.photos_path}, Videos: {self.videos_path}")
    
    def capture_photo(self, frame, custom_name=None):
        """
        Capture a photo from the current frame
        
        Args:
            frame: OpenCV frame to save
            custom_name (str): Custom filename (optional)
            
        Returns:
            str: Path to saved photo or None if failed
        """
        try:
            if frame is None:
                print("Error: No frame provided for photo capture")
                return None
            
            # Generate filename
            if custom_name:
                filename = f"{custom_name}{self.photo_format}"
            else:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"photo_{timestamp}{self.photo_format}"
            
            filepath = os.path.join(self.photos_path, filename)
            
            # Save photo with specified quality
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.photo_quality]
            success = cv2.imwrite(filepath, frame, encode_params)
            
            if success:
                self.photos_taken += 1
                print(f"Photo saved: {filepath}")
                
                # Save metadata
                self._save_photo_metadata(filepath, frame.shape)
                
                return filepath
            else:
                print(f"Failed to save photo: {filepath}")
                return None
                
        except Exception as e:
            print(f"Error capturing photo: {e}")
            return None
    
    def start_recording(self, frame_width=640, frame_height=480, custom_name=None):
        """
        Start video recording
        
        Args:
            frame_width (int): Video width
            frame_height (int): Video height
            custom_name (str): Custom filename (optional)
            
        Returns:
            bool: True if recording started successfully
        """
        try:
            if self.is_recording:
                print("Recording already in progress")
                return False
            
            # Generate filename
            if custom_name:
                filename = f"{custom_name}{self.video_format}"
            else:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"video_{timestamp}{self.video_format}"
            
            self.current_recording_path = os.path.join(self.videos_path, filename)
            
            # Set up video writer
            fourcc = cv2.VideoWriter_fourcc(*self.video_codec)
            self.video_writer = cv2.VideoWriter(
                self.current_recording_path,
                fourcc,
                self.video_fps,
                (frame_width, frame_height)
            )
            
            if not self.video_writer.isOpened():
                print("Failed to initialize video writer")
                self.video_writer = None
                return False
            
            self.is_recording = True
            self.recording_start_time = time.time()
            
            print(f"Recording started: {self.current_recording_path}")
            return True
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_recording = False
            self.video_writer = None
            return False
    
    def record_frame(self, frame):
        """
        Add a frame to the current recording
        
        Args:
            frame: OpenCV frame to record
            
        Returns:
            bool: True if frame was recorded successfully
        """
        try:
            if not self.is_recording or self.video_writer is None:
                return False
            
            if frame is None:
                return False
            
            # Write frame to video
            self.video_writer.write(frame)
            return True
            
        except Exception as e:
            print(f"Error recording frame: {e}")
            return False
    
    def stop_recording(self):
        """
        Stop video recording
        
        Returns:
            str: Path to saved video or None if failed
        """
        try:
            if not self.is_recording:
                print("No recording in progress")
                return None
            
            self.is_recording = False
            
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None
            
            # Calculate recording duration
            if hasattr(self, 'recording_start_time'):
                duration = time.time() - self.recording_start_time
                self.total_recording_time += duration
            else:
                duration = 0
            
            self.videos_recorded += 1
            
            print(f"Recording stopped: {self.current_recording_path}")
            print(f"Duration: {duration:.1f} seconds")
            
            # Save metadata
            if self.current_recording_path:
                self._save_video_metadata(self.current_recording_path, duration)
            
            return self.current_recording_path
            
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return None
    
    def _save_photo_metadata(self, photo_path, frame_shape):
        """Save metadata for a photo"""
        try:
            metadata = {
                'filename': os.path.basename(photo_path),
                'timestamp': datetime.datetime.now().isoformat(),
                'resolution': f"{frame_shape[1]}x{frame_shape[0]}",
                'format': self.photo_format,
                'quality': self.photo_quality,
                'file_size': os.path.getsize(photo_path)
            }
            
            metadata_path = photo_path.replace(self.photo_format, '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            print(f"Error saving photo metadata: {e}")
    
    def _save_video_metadata(self, video_path, duration):
        """Save metadata for a video"""
        try:
            metadata = {
                'filename': os.path.basename(video_path),
                'timestamp': datetime.datetime.now().isoformat(),
                'duration': duration,
                'fps': self.video_fps,
                'codec': self.video_codec,
                'format': self.video_format,
                'file_size': os.path.getsize(video_path)
            }
            
            metadata_path = video_path.replace(self.video_format, '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            print(f"Error saving video metadata: {e}")
    
    def get_statistics(self):
        """Get capture statistics"""
        return {
            'photos_taken': self.photos_taken,
            'videos_recorded': self.videos_recorded,
            'total_recording_time': self.total_recording_time,
            'photos_path': self.photos_path,
            'videos_path': self.videos_path
        }
    
    def list_photos(self, limit=None):
        """List captured photos"""
        try:
            photos = []
            for file in sorted(os.listdir(self.photos_path), reverse=True):
                if file.endswith(self.photo_format):
                    photos.append({
                        'filename': file,
                        'path': os.path.join(self.photos_path, file),
                        'size': os.path.getsize(os.path.join(self.photos_path, file)),
                        'created': os.path.getctime(os.path.join(self.photos_path, file))
                    })
            
            return photos[:limit] if limit else photos
            
        except Exception as e:
            print(f"Error listing photos: {e}")
            return []
    
    def list_videos(self, limit=None):
        """List recorded videos"""
        try:
            videos = []
            for file in sorted(os.listdir(self.videos_path), reverse=True):
                if file.endswith(self.video_format):
                    videos.append({
                        'filename': file,
                        'path': os.path.join(self.videos_path, file),
                        'size': os.path.getsize(os.path.join(self.videos_path, file)),
                        'created': os.path.getctime(os.path.join(self.videos_path, file))
                    })
            
            return videos[:limit] if limit else videos
            
        except Exception as e:
            print(f"Error listing videos: {e}")
            return []
    
    def cleanup_old_files(self, max_photos=100, max_videos=20):
        """Clean up old files to save space"""
        try:
            # Clean up old photos
            photos = self.list_photos()
            if len(photos) > max_photos:
                for photo in photos[max_photos:]:
                    os.remove(photo['path'])
                    # Remove metadata file if exists
                    metadata_path = photo['path'].replace(self.photo_format, '_metadata.json')
                    if os.path.exists(metadata_path):
                        os.remove(metadata_path)
                print(f"Cleaned up {len(photos) - max_photos} old photos")
            
            # Clean up old videos
            videos = self.list_videos()
            if len(videos) > max_videos:
                for video in videos[max_videos:]:
                    os.remove(video['path'])
                    # Remove metadata file if exists
                    metadata_path = video['path'].replace(self.video_format, '_metadata.json')
                    if os.path.exists(metadata_path):
                        os.remove(metadata_path)
                print(f"Cleaned up {len(videos) - max_videos} old videos")
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def get_storage_info(self):
        """Get storage usage information"""
        try:
            photos_size = sum(f['size'] for f in self.list_photos())
            videos_size = sum(f['size'] for f in self.list_videos())
            
            return {
                'photos_count': len(self.list_photos()),
                'videos_count': len(self.list_videos()),
                'photos_size_mb': photos_size / (1024 * 1024),
                'videos_size_mb': videos_size / (1024 * 1024),
                'total_size_mb': (photos_size + videos_size) / (1024 * 1024)
            }
            
        except Exception as e:
            print(f"Error getting storage info: {e}")
            return {}


# Global instance
media_capture = None

def init_media_capture(base_path=None):
    """Initialize global media capture instance"""
    global media_capture
    try:
        media_capture = MediaCapture(base_path)
        return True
    except Exception as e:
        print(f"Failed to initialize media capture: {e}")
        return False

def get_media_capture():
    """Get the global media capture instance"""
    global media_capture
    if media_capture is None:
        init_media_capture()
    return media_capture


# Test function
if __name__ == "__main__":
    # Test media capture
    capture = MediaCapture()
    
    # Test with webcam if available
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Cannot open camera")
            exit()
        
        frame_count = 0
        recording_started = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Cannot read frame")
                break
            
            frame_count += 1
            
            # Test photo capture every 100 frames
            if frame_count % 100 == 0:
                photo_path = capture.capture_photo(frame)
                if photo_path:
                    print(f"Photo captured: {photo_path}")
            
            # Test video recording
            if frame_count == 200 and not recording_started:
                success = capture.start_recording(frame.shape[1], frame.shape[0])
                if success:
                    print("Video recording started")
                    recording_started = True
            
            if recording_started:
                capture.record_frame(frame)
            
            if frame_count == 400 and recording_started:
                video_path = capture.stop_recording()
                if video_path:
                    print(f"Video saved: {video_path}")
                break
            
            cv2.imshow('Media Capture Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):  # Take photo
                photo_path = capture.capture_photo(frame)
                if photo_path:
                    print(f"Photo captured: {photo_path}")
            elif key == ord('r'):  # Start recording
                if not capture.is_recording:
                    success = capture.start_recording(frame.shape[1], frame.shape[0])
                    if success:
                        print("Recording started")
                else:
                    video_path = capture.stop_recording()
                    if video_path:
                        print(f"Recording stopped: {video_path}")
        
        # Cleanup
        if capture.is_recording:
            capture.stop_recording()
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Print statistics
        stats = capture.get_statistics()
        print(f"Session statistics: {stats}")
        
    except Exception as e:
        print(f"Test failed: {e}")