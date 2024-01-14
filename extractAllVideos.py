import os
import cv2
import poseModule as pm
import mediapipe as mp
import json

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity = 0, min_detection_confidence = 0.5, min_tracking_confidence = 0.5)

detector = pm.poseDetector()

cwd = os.getcwd().replace("\\", "/") + "/"

onlyfiles = [f for f in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, f))]

onlyfiles.remove("extractAllVideos.py")
onlyfiles.remove("poseModule.py")

for x in onlyfiles:
    cap = cv2.VideoCapture(cwd + x)
    print(cwd + x)

    fps = round(cap.get(cv2.CAP_PROP_FPS), 0)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    timestamps = [cap.get(cv2.CAP_PROP_POS_MSEC)]

    lmList_user = []

    while cap.isOpened():
        success, image = cap.read()

        if success:
            image = detector.findPose(image)

            timestamps = [int(cap.get(cv2.CAP_PROP_POS_MSEC))]

            if timestamps[-1] % 1001 == 0:
                print(fps, total_frames, timestamps)

                lmList = detector.findPosition(image)

                for y in lmList:
                    lmList_user.append(y)

        else:
            cap.release()

    f = open(x + ".json", "x")

    with open(x + ".json", "w") as f:
        json.dump(lmList_user, f)

    f.close()

cv2.destroyAllWindows()