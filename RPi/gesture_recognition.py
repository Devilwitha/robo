#!/usr/bin/env python
"""
Gesture Recognition Module for WAVEGO Robot
Using MediaPipe for hand gesture and pose detection

Features:
- Hand gesture recognition (thumbs up, peace sign, etc.)
- Body pose detection 
- Real-time gesture tracking
- Robot control via gestures
- Confidence-based filtering
"""

import cv2
import numpy as np
import time

# MediaPipe imports with fallback
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    print("MediaPipe loaded successfully")
except ImportError:
    print("Warning: MediaPipe not available. Install with: pip install mediapipe")
    MEDIAPIPE_AVAILABLE = False
    mp = None


class GestureRecognition:
    def __init__(self, enable_hands=True, enable_pose=True, confidence=0.7):
        """
        Initialize Gesture Recognition
        
        Args:
            enable_hands (bool): Enable hand detection
            enable_pose (bool): Enable pose detection  
            confidence (float): Minimum confidence for detections
        """
        self.enable_hands = enable_hands
        self.enable_pose = enable_pose
        self.confidence = confidence
        
        # MediaPipe setup
        if MEDIAPIPE_AVAILABLE:
            self.mp_hands = mp.solutions.hands if enable_hands else None
            self.mp_pose = mp.solutions.pose if enable_pose else None
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles
            
            # Initialize MediaPipe modules
            if self.mp_hands:
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=confidence,
                    min_tracking_confidence=confidence
                )
            else:
                self.hands = None
                
            if self.mp_pose:
                self.pose = self.mp_pose.Pose(
                    static_image_mode=False,
                    min_detection_confidence=confidence,
                    min_tracking_confidence=confidence
                )
            else:
                self.pose = None
        else:
            self.hands = None
            self.pose = None
        
        # Gesture state tracking
        self.last_gesture = None
        self.gesture_start_time = 0
        self.gesture_hold_time = 1.0  # Seconds to hold gesture for recognition
        
        # Known gestures
        self.gesture_names = {
            'thumbs_up': 'Thumbs Up',
            'thumbs_down': 'Thumbs Down', 
            'peace': 'Peace Sign',
            'stop': 'Stop Hand',
            'point': 'Pointing',
            'fist': 'Fist',
            'open_hand': 'Open Hand',
            'ok_sign': 'OK Sign'
        }
        
        print(f"Gesture Recognition initialized (MediaPipe: {MEDIAPIPE_AVAILABLE})")
    
    def detect_gestures(self, frame):
        """
        Detect gestures in the given frame
        
        Args:
            frame: Input image frame
            
        Returns:
            results: Dictionary with detected gestures and poses
        """
        if not MEDIAPIPE_AVAILABLE:
            return {'hands': [], 'pose': None, 'gestures': []}
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = {
            'hands': [],
            'pose': None,
            'gestures': []
        }
        
        try:
            # Hand detection
            if self.hands:
                hand_results = self.hands.process(rgb_frame)
                if hand_results.multi_hand_landmarks:
                    for idx, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
                        # Get hand classification (left/right)
                        hand_label = hand_results.multi_handedness[idx].classification[0].label
                        
                        # Analyze hand gesture
                        gesture = self._analyze_hand_gesture(hand_landmarks)
                        
                        results['hands'].append({
                            'landmarks': hand_landmarks,
                            'label': hand_label,
                            'gesture': gesture
                        })
                        
                        results['gestures'].append(gesture)
            
            # Pose detection
            if self.pose:
                pose_results = self.pose.process(rgb_frame)
                if pose_results.pose_landmarks:
                    pose_gesture = self._analyze_pose_gesture(pose_results.pose_landmarks)
                    results['pose'] = {
                        'landmarks': pose_results.pose_landmarks,
                        'gesture': pose_gesture
                    }
                    if pose_gesture:
                        results['gestures'].append(pose_gesture)
        
        except Exception as e:
            print(f"Error in gesture detection: {e}")
        
        return results
    
    def _analyze_hand_gesture(self, hand_landmarks):
        """Analyze hand landmarks to determine gesture"""
        try:
            # Get landmark positions
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append([lm.x, lm.y])
            
            landmarks = np.array(landmarks)
            
            # Hand landmark indices (MediaPipe hand model)
            THUMB_TIP = 4
            THUMB_IP = 3
            INDEX_TIP = 8
            INDEX_PIP = 6
            MIDDLE_TIP = 12
            MIDDLE_PIP = 10
            RING_TIP = 16
            RING_PIP = 14
            PINKY_TIP = 20
            PINKY_PIP = 18
            WRIST = 0
            
            # Calculate finger states (extended or not)
            fingers = []
            
            # Thumb (special case - compare x coordinates)
            if landmarks[THUMB_TIP][0] > landmarks[THUMB_IP][0]:  # Right hand
                fingers.append(1 if landmarks[THUMB_TIP][0] > landmarks[THUMB_IP][0] else 0)
            else:  # Left hand
                fingers.append(1 if landmarks[THUMB_TIP][0] < landmarks[THUMB_IP][0] else 0)
            
            # Other fingers (compare y coordinates)
            finger_tips = [INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]
            finger_pips = [INDEX_PIP, MIDDLE_PIP, RING_PIP, PINKY_PIP]
            
            for tip, pip in zip(finger_tips, finger_pips):
                if landmarks[tip][1] < landmarks[pip][1]:  # Tip above PIP = extended
                    fingers.append(1)
                else:
                    fingers.append(0)
            
            # Gesture recognition based on finger states
            return self._classify_gesture(fingers, landmarks)
            
        except Exception as e:
            print(f"Error analyzing hand gesture: {e}")
            return None
    
    def _classify_gesture(self, fingers, landmarks):
        """Classify gesture based on finger states"""
        try:
            # fingers = [thumb, index, middle, ring, pinky]
            
            if fingers == [1, 0, 0, 0, 0]:  # Only thumb up
                return 'thumbs_up'
            elif fingers == [0, 0, 0, 0, 0]:  # All fingers down
                return 'fist'
            elif fingers == [1, 1, 1, 1, 1]:  # All fingers up
                return 'open_hand'
            elif fingers == [0, 1, 1, 0, 0]:  # Index and middle up
                return 'peace'
            elif fingers == [0, 1, 0, 0, 0]:  # Only index up
                return 'point'
            elif fingers == [0, 0, 0, 0, 0]:  # Fist
                return 'stop'
            elif fingers == [1, 1, 0, 0, 0]:  # Thumb and index
                # Check if they form a circle (OK sign)
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                distance = np.linalg.norm(thumb_tip - index_tip)
                if distance < 0.05:  # Tips close together
                    return 'ok_sign'
            
            return 'unknown'
            
        except Exception as e:
            print(f"Error classifying gesture: {e}")
            return None
    
    def _analyze_pose_gesture(self, pose_landmarks):
        """Analyze pose landmarks to determine body gestures"""
        try:
            landmarks = []
            for lm in pose_landmarks.landmark:
                landmarks.append([lm.x, lm.y, lm.z])
            
            landmarks = np.array(landmarks)
            
            # Pose landmark indices
            LEFT_SHOULDER = 11
            RIGHT_SHOULDER = 12
            LEFT_ELBOW = 13
            RIGHT_ELBOW = 14
            LEFT_WRIST = 15
            RIGHT_WRIST = 16
            
            # Check for arms raised
            left_arm_raised = landmarks[LEFT_WRIST][1] < landmarks[LEFT_SHOULDER][1]
            right_arm_raised = landmarks[RIGHT_WRIST][1] < landmarks[RIGHT_SHOULDER][1]
            
            if left_arm_raised and right_arm_raised:
                return 'both_arms_up'
            elif left_arm_raised:
                return 'left_arm_up'
            elif right_arm_raised:
                return 'right_arm_up'
            
            return None
            
        except Exception as e:
            print(f"Error analyzing pose: {e}")
            return None
    
    def draw_gestures(self, frame, results):
        """Draw gesture detection results on frame"""
        try:
            # Draw hand landmarks and gestures
            for hand_data in results['hands']:
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    frame, 
                    hand_data['landmarks'],
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Draw gesture label
                if hand_data['gesture']:
                    gesture_name = self.gesture_names.get(hand_data['gesture'], hand_data['gesture'])
                    
                    # Get hand bounding box for label position
                    h, w, _ = frame.shape
                    landmarks = hand_data['landmarks'].landmark
                    x_coords = [lm.x * w for lm in landmarks]
                    y_coords = [lm.y * h for lm in landmarks]
                    
                    x_min, x_max = int(min(x_coords)), int(max(x_coords))
                    y_min, y_max = int(min(y_coords)), int(max(y_coords))
                    
                    # Draw gesture label
                    label = f"{hand_data['label']}: {gesture_name}"
                    cv2.putText(frame, label, (x_min, y_min - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw pose landmarks and gestures
            if results['pose']:
                # Draw pose landmarks
                self.mp_drawing.draw_landmarks(
                    frame,
                    results['pose']['landmarks'],
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
                
                # Draw pose gesture
                if results['pose']['gesture']:
                    cv2.putText(frame, f"Pose: {results['pose']['gesture']}", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Draw gesture summary
            if results['gestures']:
                y_offset = 60
                cv2.putText(frame, "Detected Gestures:", (10, y_offset), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                for i, gesture in enumerate(results['gestures'][:3]):  # Show max 3
                    if gesture:
                        y_offset += 25
                        gesture_name = self.gesture_names.get(gesture, gesture)
                        cv2.putText(frame, f"• {gesture_name}", (10, y_offset), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        except Exception as e:
            print(f"Error drawing gestures: {e}")
        
        return frame
    
    def get_robot_command(self, results):
        """Convert gestures to robot commands"""
        commands = []
        
        for gesture in results['gestures']:
            if gesture == 'thumbs_up':
                commands.append('forward')
            elif gesture == 'thumbs_down':
                commands.append('backward')
            elif gesture == 'peace':
                commands.append('jump')
            elif gesture == 'stop' or gesture == 'fist':
                commands.append('DS')  # Stop forward/backward
                commands.append('TS')  # Stop left/right
            elif gesture == 'point':
                commands.append('handshake')
            elif gesture == 'open_hand':
                commands.append('steady')
        
        # Pose commands
        if results['pose']:
            pose_gesture = results['pose']['gesture']
            if pose_gesture == 'both_arms_up':
                commands.append('jump')
            elif pose_gesture == 'left_arm_up':
                commands.append('left')
            elif pose_gesture == 'right_arm_up':
                commands.append('right')
        
        return commands
    
    def is_available(self):
        """Check if gesture recognition is available"""
        return MEDIAPIPE_AVAILABLE and (self.hands is not None or self.pose is not None)


# Global instance
gesture_detector = None

def init_gesture_recognition(enable_hands=True, enable_pose=True, confidence=0.7):
    """Initialize global gesture recognition instance"""
    global gesture_detector
    try:
        gesture_detector = GestureRecognition(enable_hands, enable_pose, confidence)
        return gesture_detector.is_available()
    except Exception as e:
        print(f"Failed to initialize gesture recognition: {e}")
        return False

def get_gesture_detector():
    """Get the global gesture detector instance"""
    global gesture_detector
    if gesture_detector is None:
        init_gesture_recognition()
    return gesture_detector


# Test function
if __name__ == "__main__":
    # Test gesture recognition
    detector = GestureRecognition()
    
    if not detector.is_available():
        print("Gesture recognition not available")
        exit()
    
    # Test with webcam
    try:
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect gestures
            results = detector.detect_gestures(frame)
            
            # Draw results
            frame = detector.draw_gestures(frame, results)
            
            # Get robot commands
            commands = detector.get_robot_command(results)
            if commands:
                print(f"Robot commands: {commands}")
            
            cv2.imshow('Gesture Recognition Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Test failed: {e}")