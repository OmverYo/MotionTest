import cv2
import mediapipe as mp

class poseDetector():
    # Mediapipe의 Pose Detection에서 사용될 옵션 값 지정
    def __init__(self, mode = False, upBody = False, smooth = True, detectionCon = 0.85, trackCon = 0.85):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, model_complexity = 0, min_detection_confidence = 0.5, min_tracking_confidence = 0.5)

    # 카메라 앞 인물이 있는지 인식
    def findPose(self, img, draw = False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return img

    # 카메라 앞 인식된 인물의 좌표 값을 추출, 머리 제외
    def findPosition(self, img, draw = False):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                if id not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                    h, w, c = img.shape
                    # print(id, lm)
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lmList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lmList
    
    # 상체만 추출
    def findTop(self, img, draw = False):
        self.topList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                if id in [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]:
                    h, w, c = img.shape
                    # print(id, lm)
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.topList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.topList
    
    # 하체만 추출
    def findBottom(self, img, draw = False):
        self.bottomList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                if id in [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]:
                    h, w, c = img.shape
                    # print(id, lm)
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.bottomList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.bottomList
    
    # 손만 추출
    def findHand(self, img, draw = False):
        self.handList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                if id in [15, 16]:
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.handList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.handList
    
    # 발목만 추출
    def findAnkle(self, img, draw = False):
        self.ankleList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                if id in [27, 28]:
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.ankleList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.ankleList
    
    # 엉덩이만 추출
    def findHip(self, img, draw = False):
        self.hipList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                if id in [23, 27]:
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.hipList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.hipList

    # 무릎 올리며 펀칭을 위해 어깨 손 엉덩이 무릎 추출
    def findKnee(self, img, draw = False):
        self.kneeList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                if id in [11, 12, 15, 16, 23, 24, 25, 26]:
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.kneeList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.kneeList
    
    # 평형성을 위해 어깨 엉덩이 무릎 추출
    def findKneeHip(self, img, draw = False):
        self.kneeHipList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                if id in [11, 12, 23, 24, 25, 26]:
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.kneeHipList.append([cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.kneeHipList