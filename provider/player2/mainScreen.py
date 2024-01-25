import cv2
from provider import poseModule as pm
from provider import api

def mainScreen():
    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    while user_cam.isOpened():
        ret_val, image = user_cam.read()
        flipFrame = cv2.flip(image, 1)

        # image_1 = detector.findPose(image_1)
        # handList_user = detector.findHand(image_1)
        # value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]
        # api.gamedata_api("/HandData/1", "PUT", value)

        ret_val, buffer = cv2.imencode('.jpg', flipFrame)
        encodedImage = buffer.tobytes()
        yield (b'--image\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encodedImage + b'\r\n')

    user_cam.release()