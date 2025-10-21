import os
import cv2
from base_camera import BaseCamera
import numpy as np
import robot
import datetime
import time
import threading
# Optional import - graceful fallback if not available
try:
    import imutils
    IMUTILS_AVAILABLE = True
except ImportError:
    print("Warning: imutils not available. Some features may be limited.")
    IMUTILS_AVAILABLE = False
    # Create a fallback imutils module
    class MockImutils:
        @staticmethod
        def grab_contours(contours):
            # Fallback for older OpenCV versions
            if len(contours) == 2:
                return contours[0]
            elif len(contours) == 3:
                return contours[1]
            else:
                return contours
    imutils = MockImutils()

# Optional camera import
try:
    from picamera2 import Picamera2 # NEUER IMPORT
    PICAMERA2_AVAILABLE = True
except ImportError:
    print("Warning: picamera2 not available. Camera functions may be limited.")
    PICAMERA2_AVAILABLE = False
    Picamera2 = None

# BollshiiOs import - optional and delayed to avoid circular imports
try:
    import BollshiiOs
    BOLLSHIIOS_AVAILABLE = True
except ImportError:
    print("Warning: BollshiiOs not available. Gyro balance integration disabled.")
    BOLLSHIIOS_AVAILABLE = False
    BollshiiOs = None

# Motion Tracker import - try simple version first, then complex version
try:
    import SimpleMotionTracker as MotionTracker
    MOTION_TRACKER_AVAILABLE = True
    print("Using SimpleMotionTracker")
except ImportError:
    try:
        import MotionTracker
        MOTION_TRACKER_AVAILABLE = True
        print("Using MotionTracker")
    except ImportError:
        print("Warning: No motion tracker available. Motion tracking features disabled.")
        MOTION_TRACKER_AVAILABLE = False
        MotionTracker = None

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

faceCascade = cv2.CascadeClassifier(thisPath + '/haarcascade_frontalface_default.xml')

upperGlobalIP = 'UPPER IP'

linePos_1 = 440
linePos_2 = 380
lineColorSet = 255
frameRender = 1
findLineError = 20

colorUpper = np.array([44, 255, 255])
colorLower = np.array([24, 100, 100])

speedMove = 100

class CVThread(threading.Thread):
    font = cv2.FONT_HERSHEY_SIMPLEX
    # ... (der Rest dieser Klasse bleibt komplett unverÃ¤ndert) ...
    # ... ich kÃ¼rze sie hier ab, um die Ãœbersicht zu wahren.
    # Du musst hier nichts Ã¤ndern!
    cameraDiagonalW = 64
    cameraDiagonalH = 48
    videoW = 640
    videoH = 480
    tor = 27
    aspd = 0.005


    def __init__(self, *args, **kwargs):
        self.CVThreading = 0
        self.CVMode = 'none'
        self.imgCV = None
        self.faces = None

        self.mov_x = None
        self.mov_y = None
        self.mov_w = None
        self.mov_h = None

        self.radius = 0
        self.box_x = None
        self.box_y = None
        self.drawing = 0

        self.findColorDetection = 0

        self.left_Pos1 = None
        self.right_Pos1 = None
        self.center_Pos1 = None

        self.left_Pos2 = None
        self.right_Pos2 = None
        self.center_Pos2 = None

        self.center = None

        super(CVThread, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()

        self.avg = None
        self.motionCounter = 0
        self.lastMovtionCaptured = datetime.datetime.now()
        self.frameDelta = None
        self.thresh = None
        self.cnts = None

        self.CVCommand = 'forward'


    def mode(self, invar, imgInput):
        self.CVMode = invar
        self.imgCV = imgInput
        self.resume()


    def elementDraw(self,imgInput):
        if self.CVMode == 'none':
            pass

        elif self.CVMode == 'faceDetection':
            if len(self.faces):
                if len(self.faces) == 1:
                    cv2.putText(imgInput,'1 Face Detected',(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
                else:
                    cv2.putText(imgInput,'%d Faces Detected'%len(self.faces),(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
            else:
                cv2.putText(imgInput,'Face Detecting',(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
            for (x,y,w,h) in self.faces:
                cv2.rectangle(imgInput,(x,y),(x+w,y+h),(64,128,255),2)

        elif self.CVMode == 'findColor':
            if self.findColorDetection:
                cv2.putText(imgInput,'Target Detected',(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
                self.drawing = 1
            else:
                cv2.putText(imgInput,'Target Detecting',(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
                self.drawing = 0

            if self.radius > 10 and self.drawing:
                cv2.rectangle(imgInput,(int(self.box_x-self.radius),int(self.box_y+self.radius)),(int(self.box_x+self.radius),int(self.box_y-self.radius)),(255,255,255),1)

        elif self.CVMode == 'findlineCV':
            if frameRender:
                imgInput = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)
                retval_bw, imgInput =  cv2.threshold(imgInput, 0, 255, cv2.THRESH_OTSU)
                imgInput = cv2.erode(imgInput, None, iterations=6)
            try:
                if lineColorSet == 255:
                    cv2.putText(imgInput,('Following White Line'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
                    cv2.putText(imgInput,('Following White Line'),(230,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),1,cv2.LINE_AA)
                else:
                    cv2.putText(imgInput,('Following Black Line'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
                    cv2.putText(imgInput,('Following Black Line'),(230,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),1,cv2.LINE_AA)

                cv2.putText(imgInput,(self.CVCommand),(30,90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
                cv2.putText(imgInput,(self.CVCommand),(230,90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),1,cv2.LINE_AA)

                cv2.line(imgInput,(self.left_Pos1,(linePos_1+30)),(self.left_Pos1,(linePos_1-30)),(255,255,255),1)
                cv2.line(imgInput,((self.left_Pos1+1),(linePos_1+30)),((self.left_Pos1+1),(linePos_1-30)),(0,0,0),1)

                cv2.line(imgInput,(self.right_Pos1,(linePos_1+30)),(self.right_Pos1,(linePos_1-30)),(255,255,255),1)
                cv2.line(imgInput,((self.right_Pos1-1),(linePos_1+30)),((self.right_Pos1-1),(linePos_1-30)),(0,0,0),1)

                cv2.line(imgInput,(0,linePos_1),(640,linePos_1),(255,255,255),1)
                cv2.line(imgInput,(0,linePos_1+1),(640,linePos_1+1),(0,0,0),1)

                cv2.line(imgInput,(320-findLineError,0),(320-findLineError,480),(255,255,255),1)
                cv2.line(imgInput,(320+findLineError,0),(320+findLineError,480),(255,255,255),1)

                cv2.line(imgInput,(320-findLineError+1,0),(320-findLineError+1,480),(0,0,0),1)
                cv2.line(imgInput,(320+findLineError-1,0),(320+findLineError-1,480),(0,0,0),1)

                cv2.line(imgInput,(self.left_Pos2,(linePos_2+30)),(self.left_Pos2,(linePos_2-30)),(255,255,255),1)
                cv2.line(imgInput,(self.right_Pos2,(linePos_2+30)),(self.right_Pos2,(linePos_2-30)),(255,255,255),1)
                cv2.line(imgInput,(0,linePos_2),(640,linePos_2),(255,255,255),1)

                cv2.line(imgInput,(self.left_Pos2+1,(linePos_2+30)),(self.left_Pos2+1,(linePos_2-30)),(0,0,0),1)
                cv2.line(imgInput,(self.right_Pos2-1,(linePos_2+30)),(self.right_Pos2-1,(linePos_2-30)),(0,0,0),1)
                cv2.line(imgInput,(0,linePos_2+1),(640,linePos_2+1),(0,0,0),1)

                cv2.line(imgInput,((self.center-20),int((linePos_1+linePos_2)/2)),((self.center+20),int((linePos_1+linePos_2)/2)),(0,0,0),1)
                cv2.line(imgInput,((self.center),int((linePos_1+linePos_2)/2+20)),((self.center),int((linePos_1+linePos_2)/2-20)),(0,0,0),1)

                cv2.line(imgInput,((self.center-20),int((linePos_1+linePos_2)/2+1)),((self.center+20),int((linePos_1+linePos_2)/2+1)),(255,255,255),1)
                cv2.line(imgInput,((self.center+1),int((linePos_1+linePos_2)/2+20)),((self.center+1),int((linePos_1+linePos_2)/2-20)),(255,255,255),1)
            except:
                pass

        elif self.CVMode == 'watchDog':
            if self.drawing:
                cv2.putText(imgInput,'Motion Detected',(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
                robot.buzzerCtrl(1, 0)
                robot.lightCtrl('red', 0)
                cv2.rectangle(imgInput, (self.mov_x, self.mov_y), (self.mov_x + self.mov_w, self.mov_y + self.mov_h), (128, 255, 0), 1)
            else:
                cv2.putText(imgInput,'Motion Detecting',(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
                robot.buzzerCtrl(0, 0)
                robot.lightCtrl('blue', 0)

        elif self.CVMode == 'motionTracking':
            # PERSON FOLLOWING with Distance Control - Follow owner and stop at safe distance
            try:
                # Initialize person following variables
                if not hasattr(self, 'motion_bg'):
                    self.motion_bg = None
                    self.following_active = True
                    self.last_person_center = None
                    self.last_person_area = 0
                    self.follow_distance_min = 8000    # Minimum area - too close, stop
                    self.follow_distance_max = 3000    # Maximum area - too far, follow
                    self.person_lost_counter = 0
                    self.max_lost_frames = 30  # Stop following after 30 frames without person
                
                # Convert to grayscale
                gray = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                
                # Initialize background model
                if self.motion_bg is None:
                    self.motion_bg = gray.copy().astype("float")
                    cv2.putText(imgInput,'PERSON FOLLOWING: Initializing...',(40,60), CVThread.font, 0.6,(0,255,255),2,cv2.LINE_AA)
                    return imgInput
                
                # Update background model slowly to detect person movement
                cv2.accumulateWeighted(gray, self.motion_bg, 0.3)
                
                # Calculate frame difference
                frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(self.motion_bg))
                thresh = cv2.threshold(frame_delta, 30, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=3)
                
                # Find contours (potential person)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                person_detected = False
                person_center = None
                person_area = 0
                largest_area = 0
                
                # Find largest movement (assume it's the person to follow)
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 1500:  # Minimum size for person detection
                        if area > largest_area:
                            largest_area = area
                            person_area = area
                            person_detected = True
                            x, y, w, h = cv2.boundingRect(contour)
                            person_center = (x + w//2, y + h//2)
                            
                            # Draw person detection
                            cv2.rectangle(imgInput, (x, y), (x + w, y + h), (0, 255, 0), 3)
                            cv2.circle(imgInput, person_center, 20, (0, 0, 255), -1)
                
                # Person Following Logic
                if person_detected and person_center:
                    # Person found - reset lost counter
                    self.person_lost_counter = 0
                    self.last_person_center = person_center
                    self.last_person_area = person_area
                    
                    # Calculate distance based on detected area (larger area = closer person)
                    frame_center_x = imgInput.shape[1] // 2
                    center_x = person_center[0]
                    
                    # Distance control logic
                    if person_area > self.follow_distance_min:
                        # PERSON TOO CLOSE - STOP AND WAIT
                        robot.stopLR()
                        robot.stopFB()
                        cv2.putText(imgInput,'PERSON TOO CLOSE - STOPPING',(40,60), CVThread.font, 0.6,(255,0,0),2,cv2.LINE_AA)
                        cv2.putText(imgInput,f'Distance: {int(person_area)} (Min: {self.follow_distance_min})',(40,90), CVThread.font, 0.5,(255,0,0),1,cv2.LINE_AA)
                        cv2.putText(imgInput,'Waiting for person to move away...',(40,120), CVThread.font, 0.4,(255,0,0),1,cv2.LINE_AA)
                        
                    elif person_area < self.follow_distance_max:
                        # PERSON TOO FAR - FOLLOW
                        cv2.putText(imgInput,'PERSON TOO FAR - FOLLOWING',(40,60), CVThread.font, 0.6,(0,255,0),2,cv2.LINE_AA)
                        cv2.putText(imgInput,f'Distance: {int(person_area)} (Max: {self.follow_distance_max})',(40,90), CVThread.font, 0.5,(0,255,0),1,cv2.LINE_AA)
                        
                        # Movement logic - center on person first, then move forward
                        if center_x < frame_center_x - 80:
                            robot.left(25)
                            cv2.putText(imgInput,'CENTERING: TURN LEFT',(40,120), CVThread.font, 0.5,(255,255,0),2,cv2.LINE_AA)
                        elif center_x > frame_center_x + 80:
                            robot.right(25)
                            cv2.putText(imgInput,'CENTERING: TURN RIGHT',(40,120), CVThread.font, 0.5,(255,255,0),2,cv2.LINE_AA)
                        else:
                            robot.forward(20)  # Slow forward movement
                            cv2.putText(imgInput,'FOLLOWING: MOVE FORWARD',(40,120), CVThread.font, 0.5,(255,255,0),2,cv2.LINE_AA)
                    
                    else:
                        # PERFECT DISTANCE - JUST TRACK
                        robot.stopLR()
                        robot.stopFB()
                        cv2.putText(imgInput,'PERFECT DISTANCE - TRACKING',(40,60), CVThread.font, 0.6,(0,255,255),2,cv2.LINE_AA)
                        cv2.putText(imgInput,f'Distance: {int(person_area)} (OPTIMAL)',(40,90), CVThread.font, 0.5,(0,255,255),1,cv2.LINE_AA)
                        
                        # Still center on person even when at perfect distance
                        if center_x < frame_center_x - 100:
                            robot.left(15)
                            cv2.putText(imgInput,'FINE TUNING: TURN LEFT',(40,120), CVThread.font, 0.4,(0,255,255),1,cv2.LINE_AA)
                        elif center_x > frame_center_x + 100:
                            robot.right(15)
                            cv2.putText(imgInput,'FINE TUNING: TURN RIGHT',(40,120), CVThread.font, 0.4,(0,255,255),1,cv2.LINE_AA)
                        else:
                            cv2.putText(imgInput,'PERSON CENTERED - STANDING BY',(40,120), CVThread.font, 0.4,(0,255,255),1,cv2.LINE_AA)
                
                else:
                    # NO PERSON DETECTED
                    self.person_lost_counter += 1
                    
                    if self.person_lost_counter < self.max_lost_frames:
                        # PERSON TEMPORARILY LOST - KEEP LOOKING
                        cv2.putText(imgInput,'SEARCHING FOR PERSON...',(40,60), CVThread.font, 0.6,(255,255,0),2,cv2.LINE_AA)
                        cv2.putText(imgInput,f'Lost frames: {self.person_lost_counter}/{self.max_lost_frames}',(40,90), CVThread.font, 0.4,(255,255,0),1,cv2.LINE_AA)
                        
                        # If we had a last known position, slowly turn to look for person
                        if self.last_person_center:
                            cv2.putText(imgInput,f'Last seen at: {self.last_person_center}',(40,120), CVThread.font, 0.4,(255,255,0),1,cv2.LINE_AA)
                            cv2.circle(imgInput, self.last_person_center, 30, (255, 255, 0), 2)
                        
                        robot.stopLR()
                        robot.stopFB()
                        
                    else:
                        # PERSON LOST FOR TOO LONG - STOP FOLLOWING
                        cv2.putText(imgInput,'PERSON LOST - STANDING BY',(40,60), CVThread.font, 0.6,(255,0,255),2,cv2.LINE_AA)
                        cv2.putText(imgInput,'Move in front of camera to resume following',(40,90), CVThread.font, 0.4,(255,0,255),1,cv2.LINE_AA)
                        cv2.putText(imgInput,'Robot will wait here...',(40,120), CVThread.font, 0.4,(255,0,255),1,cv2.LINE_AA)
                        
                        robot.stopLR()
                        robot.stopFB()
                
                # Draw distance zones for visualization
                cv2.putText(imgInput,f'Distance Zones: Close>{self.follow_distance_min} | Optimal:{self.follow_distance_max}-{self.follow_distance_min} | Far<{self.follow_distance_max}',(10,imgInput.shape[0]-20), CVThread.font, 0.3,(255,255,255),1,cv2.LINE_AA)
                
            except Exception as e:
                cv2.putText(imgInput,f'PERSON FOLLOWING ERROR: {str(e)[:40]}',(40,60), CVThread.font, 0.5,(0,0,255),2,cv2.LINE_AA)
                robot.stopLR()
                robot.stopFB()

        return imgInput


    def watchDog(self, imgInput):
        timestamp = datetime.datetime.now()
        gray = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.avg is None:
            print("[INFO] starting background model...")
            self.avg = gray.copy().astype("float")
            return 'background model'

        cv2.accumulateWeighted(gray, self.avg, 0.5)
        self.frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        self.thresh = cv2.threshold(self.frameDelta, 5, 255,
            cv2.THRESH_BINARY)[1]
        self.thresh = cv2.dilate(self.thresh, None, iterations=2)
        self.cnts = cv2.findContours(self.thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        self.cnts = imutils.grab_contours(self.cnts)
        # print('x')
        # loop over the contours
        for c in self.cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 2000:
                continue
    
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (self.mov_x, self.mov_y, self.mov_w, self.mov_h) = cv2.boundingRect(c)
            self.drawing = 1
            
            self.motionCounter += 1

            self.lastMovtionCaptured = timestamp

        if (timestamp - self.lastMovtionCaptured).seconds >= 0.5:
            self.drawing = 0
            robot.buzzerCtrl(0, 0)

        self.pause()


    def findLineTest(self, posInput, setCenter):#2
        if not posInput:
            robot.robotCtrl.moveStart(speedMove, 'no', 'no')
            return

        if posInput > (setCenter + findLineError):
            self.CVCommand = 'Turning Right'

        elif posInput < (setCenter - findLineError):
            self.CVCommand = 'Turning Left'

        else:
            self.CVCommand = 'Forward'


    def findLineCtrl(self, posInput, setCenter):#2
        if not posInput:
            robot.robotCtrl.moveStart(speedMove, 'no', 'no')
            return

        if posInput > (setCenter + findLineError):
            #turnRight
            robot.right()
            self.CVCommand = 'Turning Right'
            print('Turning Right')

        elif posInput < (setCenter - findLineError):
            #turnLeft
            robot.left()
            self.CVCommand = 'Turning Left'
            print('Turning Left')

        else:
            #forward
            robot.forward()
            self.CVCommand = 'Forward'
            print('Forward')


    def findlineCV(self, frame_image):
        frame_findline = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
        retval, frame_findline =  cv2.threshold(frame_findline, 0, 255, cv2.THRESH_OTSU)
        frame_findline = cv2.erode(frame_findline, None, iterations=6)
        colorPos_1 = frame_findline[linePos_1]
        colorPos_2 = frame_findline[linePos_2]
        try:
            lineColorCount_Pos1 = np.sum(colorPos_1 == lineColorSet)
            lineColorCount_Pos2 = np.sum(colorPos_2 == lineColorSet)

            lineIndex_Pos1 = np.where(colorPos_1 == lineColorSet)
            lineIndex_Pos2 = np.where(colorPos_2 == lineColorSet)

            if lineColorCount_Pos1 == 0:
                lineColorCount_Pos1 = 1
            if lineColorCount_Pos2 == 0:
                lineColorCount_Pos2 = 1

            self.left_Pos1 = lineIndex_Pos1[0][lineColorCount_Pos1-1]
            self.right_Pos1 = lineIndex_Pos1[0][0]
            self.center_Pos1 = int((self.left_Pos1+self.right_Pos1)/2)

            self.left_Pos2 = lineIndex_Pos2[0][lineColorCount_Pos2-1]
            self.right_Pos2 = lineIndex_Pos2[0][0]
            self.center_Pos2 = int((self.left_Pos2+self.right_Pos2)/2)

            self.center = int((self.center_Pos1+self.center_Pos2)/2)
        except:
            center = None
            pass

        if Camera.CVMode == 'run':
            self.findLineCtrl(self.center, 320)
        else:
            self.findLineTest(self.center, 320)
        self.pause()


    def findColor(self, frame_image):
        hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, colorLower, colorUpper)#1
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        if len(cnts) > 0:
            X_LOCK = 0
            Y_LOCK = 0
            self.findColorDetection = 1
            c = max(cnts, key=cv2.contourArea)
            ((self.box_x, self.box_y), self.radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            X = int(self.box_x)
            Y = int(self.box_y)
            error_Y = abs(240 - Y)
            error_X = abs(320 - X)

            if Y < 240 - CVThread.tor:
                # error_Y*CVThread.aspd
                robot.lookUp()
            elif Y > 240 + CVThread.tor:
                robot.lookDown()
            else:
                Y_LOCK = 1

            if X < 320 - CVThread.tor:
                robot.lookLeft()
            elif X > 320 + CVThread.tor:
                robot.lookRight()
            else:
                X_LOCK = 1

            if X_LOCK == 1 and Y_LOCK == 1:
                robot.buzzerCtrl(1, 0)
                robot.lightCtrl('red', 0)
            else:
                robot.buzzerCtrl(0, 0)
                robot.lightCtrl('blue', 0)

        else:
            self.findColorDetection = 0
        self.pause()


    def faceDetectCV(self, frame_image):
        grayGen = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
        self.faces = faceCascade.detectMultiScale(
                grayGen,       
                scaleFactor=1.2,
                minNeighbors=5,       
                minSize=(20, 20)
            )
        if len(self.faces):
            robot.lightCtrl('red', 0)
            robot.buzzerCtrl(1, 0)
        else:
            robot.lightCtrl('blue', 0)
            robot.buzzerCtrl(0, 0)
        self.pause()


    def pause(self):
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def run(self):
        while 1:
            if self.CVMode == 'none':
                robot.buzzerCtrl(0, 0)

            self.__flag.wait()
            if self.CVMode == 'none':
                robot.stopLR()
                robot.stopFB()
                robot.buzzerCtrl(0, 0)
                robot.lightCtrl('blue', 0)
                self.pause()
                robot.buzzerCtrl(0, 0)
                continue

            elif self.CVMode == 'findColor':
                self.CVThreading = 1
                self.findColor(self.imgCV)
                self.CVThreading = 0

            elif self.CVMode == 'findlineCV':
                self.CVThreading = 1
                self.findlineCV(self.imgCV)
                self.CVThreading = 0

            elif self.CVMode == 'watchDog':
                self.CVThreading = 1
                self.watchDog(self.imgCV)
                self.CVThreading = 0

            elif self.CVMode == 'faceDetection':
                self.CVThreading = 1
                self.faceDetectCV(self.imgCV)
                self.CVThreading = 0


class Camera(BaseCamera):
    video_source = 0
    modeSelect = 'none'
    CVMode = 'run'

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    # ... (der Rest der Klasse bleibt unverÃ¤ndert) ...
    def robotStop(self):
        robot.robotCtrl.moveStart(speedMove, 'no', 'no')
        time.sleep(0.1)
        robot.robotCtrl.moveStart(speedMove, 'no', 'no')

    def colorFindSet(self, invarH, invarS, invarV):
        global colorUpper, colorLower
        HUE_1 = invarH+15
        HUE_2 = invarH-15
        if HUE_1>180:HUE_1=180
        if HUE_2<0:HUE_2=0

        SAT_1 = invarS+150
        SAT_2 = invarS-150
        if SAT_1>255:SAT_1=255
        if SAT_2<0:SAT_2=0

        VAL_1 = invarV+150
        VAL_2 = invarV-150
        if VAL_1>255:VAL_1=255
        if VAL_2<0:VAL_2=0

        colorUpper = np.array([HUE_1, SAT_1, VAL_1])
        colorLower = np.array([HUE_2, SAT_2, VAL_2])
        print('HSV_1:%d %d %d'%(HUE_1, SAT_1, VAL_1))
        print('HSV_2:%d %d %d'%(HUE_2, SAT_2, VAL_2))
        print(colorUpper)
        print(colorLower)

    def modeSet(self, invar):
        Camera.modeSelect = invar

    def upperIP(self, invar):
        global upperGlobalIP
        upperGlobalIP = invar

    def CVRunSet(self, invar):
        global CVRun
        CVRun = invar

    def linePosSet_1(self, invar):
        global linePos_1
        linePos_1 = invar

    def linePosSet_2(self, invar):
        global linePos_2
        linePos_2 = invar

    def colorSet(self, invar):
        global lineColorSet
        lineColorSet = invar

    def randerSet(self, invar):
        global frameRender
        frameRender = invar

    def errorSet(self, invar):
        global findLineError
        findLineError = invar

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    # Veraltete frames() Methode wird ersetzt
    # @staticmethod
    # def frames():
    #     camera = cv2.VideoCapture(Camera.video_source)
    #     ... (alter Code)

    # ############### NEUE METHODE ##################
    @staticmethod
    def frames():
        # picamera2 initialisieren
        picam2 = Picamera2()
        # Eine Konfiguration fÃ¼r die Kamera erstellen (640x480)
        config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        # Kamera starten
        picam2.start()
        print("INFO: picamera2 gestartet.")

        # CV-Thread initialisieren und starten
        cvt = CVThread()
        cvt.start()

        while True:
            # Ein Bild als NumPy-Array aufnehmen
            img = picam2.capture_array()

            if Camera.modeSelect == 'none':
                cvt.pause()
                robot.buzzerCtrl(0, 0)
            else:
                if not cvt.CVThreading:
                    cvt.mode(Camera.modeSelect, img)
                    cvt.resume()
                try:
                    img = cvt.elementDraw(img)
                except Exception as e:
                    print(f"Error in elementDraw: {e}")
                    pass

            # Bild als JPEG kodieren und ausgeben
            try:
                yield cv2.imencode('.jpg', img)[1].tobytes()
            except Exception as e:
                print(f"Error encoding frame: {e}")
                pass
    # ############ ENDE NEUE METHODE ################


# ... (der Rest der Datei bleibt unverÃ¤ndert) ...
def commandAct(act, inputA):
    global speedMove
    print(f'COMMAND ACT: Received command: {act}')
    
    # Handle speed control first - this is the most important fix
    if 'wsB' in str(act):
        print(f'SPEED COMMAND: Processing speed command: {act}')
        try:
            # Handle both "wsB 50" and "wsB50" formats
            if isinstance(act, str):
                # Remove 'wsB' and extract the number
                speed_str = act.replace('wsB', '').strip()
                if speed_str:
                    new_speed = int(speed_str)
                    print(f'SPEED COMMAND: Extracted speed value: {new_speed}')
                    
                    # Update both global variable and robot speed
                    speedMove = new_speed
                    success = robot.speedSet(new_speed)
                    
                    if success:
                        print(f'SPEED COMMAND: Successfully set speed to {new_speed}')
                        print(f'SPEED COMMAND: Global speedMove updated to {speedMove}')
                    else:
                        print(f'SPEED COMMAND: Failed to set robot speed to {new_speed}')
                else:
                    print(f'SPEED COMMAND: No speed value found in: {act}')
            else:
                print(f'SPEED COMMAND: Invalid command type: {type(act)}')
        except (ValueError, AttributeError) as e:
            print(f'SPEED COMMAND: Error parsing speed command "{act}": {e}')
        return  # Important: return early after handling speed command
    
    # Handle movement commands
    if act == 'forward':
        current_speed = robot.getSpeed()
        robot.forward()
        print(f'COMMAND ACT: Forward at speed {current_speed}')
    elif act == 'backward':
        current_speed = robot.getSpeed()
        robot.backward()
        print(f'COMMAND ACT: Backward at speed {current_speed}')
    elif act == 'left':
        current_speed = robot.getSpeed()
        robot.left()
        print(f'COMMAND ACT: Left at speed {current_speed}')
    elif act == 'right':
        current_speed = robot.getSpeed()
        robot.right()
        print(f'COMMAND ACT: Right at speed {current_speed}')
    elif act == 'DS':
        robot.stopFB()
    elif act == 'TS':
        robot.stopLR()

    elif act == 'up':
        robot.lookUp()
    elif act == 'down':
        robot.lookDown()
    elif act == 'UDstop':
        robot.lookStopUD()
    elif act == 'lookleft':
        robot.lookLeft()
    elif act == 'lookright':
        robot.lookRight()
    elif act == 'LRstop':
        robot.lookStopLR()

    elif act == 'jump':
        robot.jump()
    elif act == 'handshake':
        robot.handShake()
    elif act == 'steady':
        robot.steadyMode()
    elif act == 'steadyOff':
        robot.steadyMode()
    elif act == 'bolliOs':
        try:
            import BollshiiOs
            BollshiiOs.start_gyro_balance()
        except ImportError as e:
            print(f"BollshiiOs not available: {e}")
    elif act == 'bolliOsOff':
        try:
            import BollshiiOs
            BollshiiOs.stop_gyro_balance()
        except ImportError as e:
            print(f"BollshiiOs not available: {e}")

    # Motion Tracking ctrl.
    elif act == 'motionTracking':
        print("=== MOTION TRACKING ACTIVATION (INLINE VERSION) ===")
        Camera.modeSelect = 'motionTracking'
        print("Camera.modeSelect set to 'motionTracking'")
        print("Motion tracking will start processing frames")
        print("=== MOTION TRACKING ACTIVATED ===")
        
    elif act == 'motionTrackingOff':
        print("=== MOTION TRACKING DEACTIVATION ===")
        Camera.modeSelect = 'none'
        robot.stopFB()
        robot.stopLR()
        print("=== MOTION TRACKING STOPPED ===")

    # openCV ctrl.
    elif act == 'faceDetection':
        Camera.modeSelect = 'faceDetection'
    elif act == 'faceDetectionOff':
        Camera.modeSelect = 'none'
        robot.buzzerCtrl(0, 0)
    elif 'trackLine' == act:
        Camera.modeSelect = 'findlineCV'
        Camera.CVMode = 'run'
    elif 'trackLineOff' == act:
        Camera.modeSelect = 'none'
        time.sleep(0.05)
        robot.stopLR()
        time.sleep(0.05)
        robot.stopFB()
        robot.buzzerCtrl(0, 0)
