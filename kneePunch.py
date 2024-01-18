import cv2, time
import poseModule as pm
import api
import playsound as ps
import pathlib

def distanceCalculate(p1, p2):
    """p1 and p2 in format (x1, y1) and (x2, y2) tuples"""
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    
    return dis

def kneePunch():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    camDelay = False
    leftStart = 0
    rightStart = 0
    Count = 0

    end = time.time()
    start = time.time()

    while True:
        end = time.time()
        if end - start >= 3 and camDelay is False:
            camDelay = True
            api.gamedata_api("/BackgroundData", "DELETE", None)
            api.gamedata_api("/ProgramData", "POST", 1)
        if end - start >= 6:
            break
        ret_val, frame = user_cam.read()
        # frame = cv2.flip(frame, 1)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    while user_cam.isOpened():
        success, image = user_cam.read()

        try:
            image = detector.findPose(image)
            results = detector.findKnee(image)
            handList_user = detector.findHand(image)

            value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]

            # api.gamedata_api("/HandData/1", "PUT", value)

            if results is not None and len(results) >= 6:
                leftShoulder = [results[0][1], results[0][2]]
                rightShoulder = [results[1][1], results[1][2]]
                leftWrist = [results[2][1], results[2][2]]
                rightWrist = [results[3][1], results[3][2]]
                leftKnee = [results[4][1], results[4][2]]
                rightKnee = [results[5][1], results[5][2]]

                end = time.time()

                if end - start >= 59:
                    rating = 0

                    if Count >= 90:
                        rating = 1

                    else:
                        rating = 0

                    value = [0, 0, 0, Count, 0, rating]

                    api.gamedata_api("/BasicData", "POST", value)

                    user_cam.release()

                    api.gamedata_api("/ProgramData", "DELETE", None)

                    break

                if distanceCalculate(leftShoulder, leftWrist) < 65 and distanceCalculate(rightShoulder, rightKnee) > 145:
                    leftStart = 1

                elif leftStart and distanceCalculate(leftShoulder, leftWrist) > 75 and distanceCalculate(rightShoulder, rightKnee) < 137:
                    Count = Count + 1
                    leftStart = 0

                    print("Count:", Count)

                if distanceCalculate(rightShoulder, rightWrist) < 65 and distanceCalculate(leftShoulder, leftKnee) > 145:
                    rightStart = 1

                elif rightStart and distanceCalculate(rightShoulder, rightWrist) > 75 and distanceCalculate(leftShoulder, leftKnee) < 137:
                    Count = Count + 1
                    rightStart = 0

                    print("Count:", Count)

        except:
            success, image = user_cam.read()
        
        flipFrame = cv2.flip(image, 1)
        ret_val, buffer = cv2.imencode('.jpg', flipFrame)
        encodedImage = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + encodedImage + b'\r\n')

    api.gamedata_api("/ProgramData", "DELETE", None)

    user_cam.release()