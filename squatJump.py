import cv2, time
import poseModule as pm
import api
import playsound as ps
import pathlib

def distanceCalculate(p1, p2):
    """p1 and p2 in format (x1, y1) and (x2, y2) tuples"""
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    
    return dis

def squatJump():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"

    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    camDelay = False
    Start = 0
    Count = 0

    startTimer = time.time()
    endTimer = time.time()

    while True:
        endTimer = time.time()
        if endTimer - startTimer >= 3 and camDelay is False:
            camDelay = True
            api.gamedata_api("/BackgroundData", "DELETE", None)
            api.gamedata_api("/ProgramData", "POST", 1)
        if endTimer - startTimer >= 6:
            break
        ret_val, image = user_cam.read()
        flipFrame = cv2.flip(image, 1)
        ret, buffer = cv2.imencode('.jpg', flipFrame)
        frame = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    while user_cam.isOpened():
        success, image = user_cam.read()
        
        try:
            image = detector.findPose(image)
            results = detector.findHip(image)
            # handList_user = detector.findHand(image)

            # value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]

            # api.gamedata_api("/HandData/1", "PUT", value)

            if results is not None and len(results) >= 2:
                leftHip = [results[0][1], results[0][2]]
                leftAnkle = [results[1][1], results[1][2]]

                if Start == 0 and distanceCalculate(leftHip, leftAnkle) < 90:
                    Start = 1
                    print("Start Ready")

                elif Start and distanceCalculate(leftHip, leftAnkle) > 110:
                    Count = Count + 1
                    Start = 0

                    print("Count:", Count)

            endTimer = time.time()

            if endTimer - startTimer >= 29:
                rating = 0

                if Count >= 20:
                    rating = 1

                else:
                    rating = 0

                value = [0, 0, Count, 0, 0, rating]

                api.gamedata_api("/BasicData", "POST", value)

                user_cam.release()

                api.gamedata_api("/ProgramData", "DELETE", None)

                break

        except:
            success, image = user_cam.read()
        
        flipFrame = cv2.flip(image, 1)
        ret_val, buffer = cv2.imencode('.jpg', flipFrame)
        encodedImage = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + encodedImage + b'\r\n')
    
    api.gamedata_api("/ProgramData", "DELETE", None)
    
    user_cam.release()