import cv2, time
import poseModule as pm
import api
import playsound as ps
import pathlib

def distanceCalculate(p1, p2):
    """p1 and p2 in format (x1, y1) and (x2, y2) tuples"""
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    
    return dis

# 무릎부터 허리까지 거리 계산
# 백터 길이 계산법으로 X와 Y가 같을 경우 45도 기준
def angleCalculate(p1, p2):
    # 무릎부터 허리까지의 Y길이가 X보다 짧으면 45도 이상
    if (p2[1] - p1[1]) < (p2[0] - p1[0]):
        angle = True
    # 무릎부터 허리까지의 Y길이가 X보다 짧으면 45도 미만
    elif (p2[1] - p1[1]) > (p2[0] - p1[0]):
        angle = False

    return angle

def kneePunch():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    camDelay = False
    leftStart = 0
    rightStart = 0
    Count = 0

    endTimer = time.time()
    startTimer = time.time()

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
            results = detector.findKnee(image)
            
            # handList_user = detector.findHand(image)
            # value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]
            # api.gamedata_api("/HandData/1", "PUT", value)

            if results is not None and len(results) >= 6:
                leftShoulder = [results[0][1], results[0][2]]
                rightShoulder = [results[1][1], results[1][2]]
                leftWrist = [results[2][1], results[2][2]]
                rightWrist = [results[3][1], results[3][2]]
                leftHip = [results[4][1], results[4][2]]
                rightHip = [results[5][1], results[5][2]]
                leftKnee = [results[6][1], results[6][2]]
                rightKnee = [results[7][1], results[7][2]]

                endTimer = time.time()

                # 60초 동안 실행
                if endTimer - startTimer >= 59:
                    # rating = 0

                    # if Count >= 90:
                    #     rating = 1

                    # else:
                    #     rating = 0

                    value = [0, 0, 0, Count, 0, 0]
                    
                    api.gamedata_api("/BasicData", "POST", value)
                    api.gamedata_api("/BasicData/1/update_rating", "PUT", value)

                    user_cam.release()

                    api.gamedata_api("/ProgramData", "DELETE", None)

                    break
                
                # 왼손과 왼어깨의 거리가 가깝고 오른무릎이 45도 이상일때
                if distanceCalculate(leftShoulder, leftWrist) < 65 and angleCalculate(rightKnee, rightHip):
                    leftStart = 1
                    ps.playsound(path + "coin.mp3")
                # 왼손과 왼어깨의 거리가 멀고 오른쪽 무릎이 45도 미만일때
                elif leftStart and distanceCalculate(leftShoulder, leftWrist) > 75 and not angleCalculate(rightKnee, rightHip):
                    Count = Count + 1
                    leftStart = 0

                    print("Count:", Count)
                # 오른손과 오른어깨의 거리가 가깝고 왼무릎이 45도 이상일때
                if distanceCalculate(rightShoulder, rightWrist) < 65 and angleCalculate(leftKnee, leftHip):
                    rightStart = 1
                    ps.playsound(path + "coin.mp3")
                # 오른손과 오른어깨의 거리가 멀고 왼무릎이 45도 미만일때
                elif rightStart and distanceCalculate(rightShoulder, rightWrist) > 75 and not angleCalculate(leftKnee, leftHip):
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