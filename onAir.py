import cv2, time
import poseModule as pm
import api

def distanceCalculate(p1, p2):
    """Calculate Euclidean distance between two points."""
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return dis

def air():
    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    # 점프 감지 임계값 설정
    JUMP_START_THRESHOLD = 25 # 이 값을 낮추면 낮게 점프해도 점프한걸로 간주
    JUMP_END_THRESHOLD = 20

    startTimer = time.time()
    ankleInitialPosition = None
    anklePositionSet = False
    jumpStarted = False
    jumpStartTimer = 0
    jumpCount = 0
    jumpList = []

    api.gamedata_api("/ProgramData", "POST", 1)

    while user_cam.isOpened():
        success, image = user_cam.read()

        try:
            image = detector.findPose(image)
            try:
                results = detector.findAnkle(image)
                handList_user = detector.findHand(image)

                value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]

                # api.gamedata_api("/HandData/1", "PUT", value)

                leftAnkle = [results[0][1], results[0][2]]
                rightAnkle = [results[1][1], results[1][2]]

            except:
                pass

            # 초기 위치 설정
            if not anklePositionSet and time.time() - startTimer > 3:
                ankleInitialPosition = (leftAnkle, rightAnkle)
                anklePositionSet = True

            # 점프 감지
            if anklePositionSet:
                currentAnkleHeight = (leftAnkle[1] + rightAnkle[1]) / 2
                initialAnkleHeight = (ankleInitialPosition[0][1] + ankleInitialPosition[1][1]) / 2

                # 점프 시작 감지
                if not jumpStarted and currentAnkleHeight < initialAnkleHeight - JUMP_START_THRESHOLD:
                    jumpStarted = True
                    jumpStartTimer = time.time()

                # 점프 종료 감지
                elif jumpStarted and currentAnkleHeight > initialAnkleHeight - JUMP_END_THRESHOLD:
                    jumpEndTimer = time.time()
                    airTime = round((jumpEndTimer - jumpStartTimer), 3)
                    jumpList.append(airTime)
                    jumpStarted = False
                    print("Air Time:", airTime, "seconds")  # 체공시간 출력

                    jumpCount += 1

                elif jumpCount >= 2:
                    jumpList.sort()

                    rating = 0

                    if jumpList[-1] >= 0.5:
                        rating = 1

                    else:
                        rating = 0
                    
                    value = [0, jumpList[-1], 0, 0, 0, rating]

                    api.gamedata_api("/BasicData", "POST", value)

                    user_cam.release()

                    api.gamedata_api("/ProgramData", "DELETE", None)

                    break

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