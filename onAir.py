import cv2, time
import poseModule as pm
import api
import playsound as ps
import pathlib

def air():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    # 점프 감지 임계값 설정
    JUMP_START_THRESHOLD = 10 # 이 값을 낮추면 낮게 점프해도 점프한걸로 간주
    JUMP_END_THRESHOLD = 10

    camDelay = False

    startTimer = time.time()
    anklePositionSet = False
    jumpStarted = False
    jumpStartTimer = 0
    jumpCount = 0
    jumpList = []

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
            results = detector.findAnkle(image)
            
            # handList_user = detector.findHand(image)
            # value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]
            # api.gamedata_api("/HandData/1", "PUT", value)

            if results is not None and len(results) >= 2:
                leftAnkle = [results[0][1], results[0][2]]
                rightAnkle = [results[1][1], results[1][2]]

                # 초기 위치 설정
                if not anklePositionSet and time.time() - startTimer > 6:
                    leftankleInitialPosition = leftAnkle[1]
                    rightankleInitialPosition = rightAnkle[1]
                    anklePositionSet = True

                # 점프 감지
                if anklePositionSet:
                    currentleftAnkleHeight = leftAnkle[1]
                    currentrightAnkleHeight = rightAnkle[1]

                    # 두 발 모두 점프 하였을 경우 시작 감지
                    if not jumpStarted and currentleftAnkleHeight < leftankleInitialPosition - JUMP_START_THRESHOLD and currentrightAnkleHeight < rightankleInitialPosition - JUMP_START_THRESHOLD:
                        jumpStarted = True
                        jumpStartTimer = time.time()

                    # 한 발이라도 먼저 떨어진 경우 점프 종료 감지
                    elif jumpStarted and (currentrightAnkleHeight > rightankleInitialPosition - JUMP_END_THRESHOLD or currentrightAnkleHeight > rightankleInitialPosition - JUMP_START_THRESHOLD):
                        jumpEndTimer = time.time()
                        airTime = round((jumpEndTimer - jumpStartTimer), 3)
                        jumpList.append(airTime)
                        jumpStarted = False
                        print("Air Time:", airTime, "seconds")  # 체공시간 출력
                        ps.playsound(path + "coin.mp3")

                        jumpCount += 1

                    # 2번 실행 후 종료
                    elif jumpCount >= 2:
                        jumpList.sort()

                        # rating = 0

                        # if jumpList[-1] >= 0.5:
                        #     rating = 1

                        # else:
                        #     rating = 0
                        
                        value = [0, jumpList[-1], 0, 0, 0, 0]

                        api.gamedata_api("/BasicData", "POST", value)
                        api.gamedata_api("/BasicData/1/update_rating", "PUT", value)

                        break

                    else:
                        pass
            
        except:
            success, image = user_cam.read()
        
        flipFrame = cv2.flip(image, 1)
        ret_val, buffer = cv2.imencode('.jpg', flipFrame)
        encodedImage = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + encodedImage + b'\r\n')
    
    while True:
        endTimer = time.time()

        if endTimer - startTimer >= 3:
            api.gamedata_api("/ProgramData", "POST", 0)

            user_cam.release()
            
            break
        
        ret_val, image = user_cam.read()
        flipFrame = cv2.flip(image, 1)
        ret, buffer = cv2.imencode('.jpg', flipFrame)
        frame = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    api.gamedata_api("/ProgramData", "DELETE", None)

    user_cam.release()