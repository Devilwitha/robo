#!/usr/bin/env python
"""
Object Recognition Module for WAVEGO Robot
Using OpenCV DNN with pre-trained models (YOLO, MobileNet-SSD, etc.)

Features:
- Real-time object detection and classification
- Multiple object detection models support
- Confidence threshold filtering
- Bounding box visualization
- Object tracking capabilities
"""

import cv2
import numpy as np
import os
import urllib.request
import time

class ObjectRecognition:
    def __init__(self, model_type='mobilenet', confidence_threshold=0.5):
        """
        Initialize Object Recognition
        
        Args:
            model_type (str): 'mobilenet' or 'yolo' or 'coco'
            confidence_threshold (float): Minimum confidence for detections
        """
        self.model_type = model_type
        self.confidence_threshold = confidence_threshold
        self.net = None
        self.classes = []
        self.colors = None
        self.output_layers = None
        
        # Initialize the selected model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the selected object detection model"""
        try:
            if self.model_type == 'mobilenet':
                self._load_mobilenet_ssd()
            elif self.model_type == 'yolo':
                self._load_yolo()
            elif self.model_type == 'coco':
                self._load_coco_ssd()
            else:
                print(f"Warning: Unknown model type {self.model_type}, using MobileNet-SSD")
                self._load_mobilenet_ssd()
                
            print(f"Object Recognition initialized with {self.model_type} model")
            
        except Exception as e:
            print(f"Error initializing object recognition: {e}")
            self.net = None
    
    def _load_mobilenet_ssd(self):
        """Load MobileNet-SSD model (lightweight, good for Raspberry Pi)"""
        # Define paths
        curpath = os.path.dirname(os.path.realpath(__file__))
        model_dir = os.path.join(curpath, 'models')
        
        # Create models directory if it doesn't exist
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        prototxt_path = os.path.join(model_dir, 'MobileNetSSD_deploy.prototxt')
        model_path = os.path.join(model_dir, 'MobileNetSSD_deploy.caffemodel')
        
        # Download models if they don't exist
        if not os.path.exists(prototxt_path):
            print("Downloading MobileNet-SSD prototxt...")
            urllib.request.urlretrieve(
                'https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/deploy.prototxt',
                prototxt_path
            )
        
        if not os.path.exists(model_path):
            print("Downloading MobileNet-SSD model (this may take a while)...")
            urllib.request.urlretrieve(
                'https://drive.google.com/uc?id=0B3gersZ2cHIxRm5PMWRoTkdHdHc',
                model_path
            )
        
        # Load the network
        self.net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
        
        # COCO classes that MobileNet-SSD can detect
        self.classes = [
            "background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
            "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
            "sofa", "train", "tvmonitor"
        ]
        
        # Generate colors for each class
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
    
    def _load_yolo(self):
        """Load YOLO model (more accurate but heavier)"""
        curpath = os.path.dirname(os.path.realpath(__file__))
        model_dir = os.path.join(curpath, 'models', 'yolo')
        
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        config_path = os.path.join(model_dir, 'yolov3.cfg')
        weights_path = os.path.join(model_dir, 'yolov3.weights')
        names_path = os.path.join(model_dir, 'coco.names')
        
        # Create a simple fallback if files don't exist
        if not all([os.path.exists(f) for f in [config_path, weights_path, names_path]]):
            print("YOLO model files not found. Please download:")
            print("1. yolov3.cfg")
            print("2. yolov3.weights") 
            print("3. coco.names")
            print("Falling back to simpler detection...")
            self._load_simple_detector()
            return
        
        # Load YOLO
        self.net = cv2.dnn.readNet(weights_path, config_path)
        
        # Load class names
        with open(names_path, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        # Get output layer names
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        
        # Generate colors
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
    
    def _load_simple_detector(self):
        """Load a simple built-in OpenCV detector as fallback"""
        print("Using simple OpenCV cascade classifiers...")
        
        # We'll use the existing face detection as a base and extend it
        curpath = os.path.dirname(os.path.realpath(__file__))
        
        # Simple classes we can detect with OpenCV
        self.classes = ["person", "face", "car", "bicycle"]
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        
        # Load cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(
            os.path.join(curpath, 'haarcascade_frontalface_default.xml')
        )
        
        # Try to load other cascades if available
        try:
            self.car_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_car.xml')
        except:
            self.car_cascade = None
            
        self.net = "simple"  # Marker that we're using simple detection
    
    def detect_objects(self, frame):
        """
        Detect objects in the given frame
        
        Args:
            frame: Input image frame
            
        Returns:
            detections: List of (class_name, confidence, (x, y, w, h))
        """
        if self.net is None:
            return []
        
        try:
            if self.net == "simple":
                return self._detect_simple(frame)
            elif self.model_type == 'mobilenet':
                return self._detect_mobilenet(frame)
            elif self.model_type == 'yolo':
                return self._detect_yolo(frame)
            else:
                return []
        except Exception as e:
            print(f"Error in object detection: {e}")
            return []
    
    def _detect_simple(self, frame):
        """Simple detection using OpenCV cascades"""
        detections = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, h) in faces:
            detections.append(("face", 0.9, (x, y, w, h)))
        
        # Detect cars if cascade is available
        if self.car_cascade is not None:
            cars = self.car_cascade.detectMultiScale(gray, 1.1, 4)
            for (x, y, w, h) in cars:
                detections.append(("car", 0.8, (x, y, w, h)))
        
        return detections
    
    def _detect_mobilenet(self, frame):
        """Detect objects using MobileNet-SSD"""
        height, width = frame.shape[:2]
        
        # Create blob from image
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
        
        # Set input to the network
        self.net.setInput(blob)
        
        # Run forward pass
        detections = self.net.forward()
        
        results = []
        
        # Process detections
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > self.confidence_threshold:
                class_id = int(detections[0, 0, i, 1])
                
                if class_id < len(self.classes):
                    class_name = self.classes[class_id]
                    
                    # Get bounding box coordinates
                    box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                    x, y, x1, y1 = box.astype(int)
                    w, h = x1 - x, y1 - y
                    
                    results.append((class_name, confidence, (x, y, w, h)))
        
        return results
    
    def _detect_yolo(self, frame):
        """Detect objects using YOLO"""
        height, width = frame.shape[:2]
        
        # Create blob
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        
        # Set input
        self.net.setInput(blob)
        
        # Run forward pass
        outs = self.net.forward(self.output_layers)
        
        # Information to show on screen
        class_ids = []
        confidences = []
        boxes = []
        
        # Process each output
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.confidence_threshold:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply non-maximum suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, 0.4)
        
        results = []
        if len(indexes) > 0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                class_name = self.classes[class_ids[i]]
                confidence = confidences[i]
                results.append((class_name, confidence, (x, y, w, h)))
        
        return results
    
    def draw_detections(self, frame, detections):
        """
        Draw bounding boxes and labels on the frame
        
        Args:
            frame: Input image
            detections: List of detections from detect_objects()
            
        Returns:
            frame: Image with drawn detections
        """
        for class_name, confidence, (x, y, w, h) in detections:
            # Get color for this class
            if self.net == "simple":
                color = self.colors[self.classes.index(class_name)] if class_name in self.classes else (255, 255, 255)
            else:
                class_idx = self.classes.index(class_name) if class_name in self.classes else 0
                color = self.colors[class_idx]
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw label background
            cv2.rectangle(frame, (x, y - label_size[1] - 10), (x + label_size[0], y), color, -1)
            
            # Draw label text
            cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame
    
    def get_detection_summary(self, detections):
        """
        Get a summary of detected objects
        
        Args:
            detections: List of detections
            
        Returns:
            summary: Dictionary with object counts
        """
        summary = {}
        for class_name, confidence, bbox in detections:
            if class_name in summary:
                summary[class_name] += 1
            else:
                summary[class_name] = 1
        
        return summary
    
    def is_available(self):
        """Check if object recognition is available"""
        return self.net is not None


# Global instance for easy access
object_detector = None

def init_object_recognition(model_type='mobilenet', confidence=0.5):
    """Initialize global object recognition instance"""
    global object_detector
    try:
        object_detector = ObjectRecognition(model_type, confidence)
        return object_detector.is_available()
    except Exception as e:
        print(f"Failed to initialize object recognition: {e}")
        return False

def get_object_detector():
    """Get the global object detector instance"""
    global object_detector
    if object_detector is None:
        init_object_recognition()
    return object_detector

# Test function
if __name__ == "__main__":
    # Test object recognition
    detector = ObjectRecognition('mobilenet')
    
    # Test with webcam if available
    try:
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect objects
            detections = detector.detect_objects(frame)
            
            # Draw detections
            frame = detector.draw_detections(frame, detections)
            
            # Show summary
            summary = detector.get_detection_summary(detections)
            if summary:
                print(f"Detected: {summary}")
            
            cv2.imshow('Object Recognition Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Test failed: {e}")