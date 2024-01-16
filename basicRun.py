import cv2, time
import poseModule as pm
import random
import api
import playsound as ps
import pathlib

def distanceCalculate(p1, p2):
    """p1 and p2 in format (x1, y1) and (x2, y2) tuples"""
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    
    return dis

def basicRun():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"

    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    randomCounter = random.randint(2, 5)

    counterResult = []

    Start = 0
    Count = 0

    api.gamedata_api("/ProgramData", "POST", 1)

    startTimer = time.time()
    endTimer = time.time()

    while user_cam.isOpened():
        success, image = user_cam.read()
        
        try:
            try:
                image = detector.findPose(image)
                results = detector.findAnkle(image)
                handList_user = detector.findHand(image)

                value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]

                # api.gamedata_api("/HandData/1", "PUT", value)

                leftAnkle = [results[0][1], results[0][2]]
                rightAnkle = [results[1][1], results[1][2]]

                print(distanceCalculate(leftAnkle, rightAnkle))

            except:
                pass

            if Count >= 3:
                y = 0

                for x in counterResult:
                    y += x

                y = round(y / 3, 3)

                rating = 0

                if y >= 0.500:
                    rating = 0

                else:
                    rating = 1

                value = [y, 0, 0, 0, 0, rating]

                api.gamedata_api("/BasicData", "POST", value)

                user_cam.release()

                api.gamedata_api("/ProgramData", "POST", 0)

                break

            if Start and int(endTimer) - int(startTimer) >= randomCounter:
                ps.playsound(path + "static/audio.mp3")

                startTimer = time.time()

            if distanceCalculate(leftAnkle, rightAnkle) < 50:
                Start = 1
                endTimer = time.time()

            elif Start and distanceCalculate(leftAnkle, rightAnkle) > 60:
                endTimer = time.time()
                
                Count = Count + 1
                Start = 0

                counterResult.append(round((endTimer - startTimer), 3))
                print("Time Taken:", round((endTimer - startTimer), 3))

                randomCounter = random.randint(2, 5)

                print("Random:", randomCounter)
                print("Count:", Count)

                startTimer = time.time()

            else:
                pass

        except:
            success, image = user_cam.read()

        ret_val, buffer = cv2.imencode('.jpg', image)

        image = buffer.tobytes()

        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
    
    api.gamedata_api("/ProgramData", "DELETE", None)
    
    user_cam.release()