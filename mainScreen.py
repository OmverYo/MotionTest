# import cv2
# import poseModule as pm
# import api
# import logging

# def mainScreen():
#     user_cam = cv2.VideoCapture(0)
#     detector = pm.poseDetector()

#     while user_cam.isOpened():
#         ret_val, image_1 = user_cam.read()

#         if not ret_val:
#             break
        
#         try:
#             image_1 = detector.findPose(image_1)
#             handList_user = detector.findHand(image_1)
#             value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]

#             ret_val, buffer = cv2.imencode('.jpg', image_1)

#             image_1 = buffer.tobytes()

#             yield (b'--image\r\n'
#                 b'Content-Type: image/jpeg\r\n\r\n' + image_1 + b'\r\n')

#             api.gamedata_api("/HandData/1", "PUT", value)

#         except:
#             ret_val, buffer = cv2.imencode('.jpg', image_1)

#             image_1 = buffer.tobytes()

#             yield (b'--image\r\n'
#                 b'Content-Type: image/jpeg\r\n\r\n' + image_1 + b'\r\n')

#     user_cam.release()

# import cv2
# import poseModule as pm
# import api
# import logging

# def mainScreen():
#     user_cam = cv2.VideoCapture(0)
#     detector = pm.poseDetector()

#     while user_cam.isOpened():
#         ret_val, image_1 = user_cam.read()

#         image_1 = detector.findPose(image_1)
#         handList_user = detector.findHand(image_1)
#         value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]

#         ret_val, buffer = cv2.imencode('.jpg', image_1)

#         image_1 = buffer.tobytes()

#         yield (b'--image\r\n'
#             b'Content-Type: image/jpeg\r\n\r\n' + image_1 + b'\r\n')
        
#         api.gamedata_api("/HandData/1", "PUT", value)

#         # except Exception as e:
#         #     logging.error("An error occurred: %s", e)

#         # # result 값이 None이어도 계속 진행
#         # if result is None:
#         #     logging.error("API call failed or returned None")
#         #     continue

#     user_cam.release()

import cv2
import poseModule as pm
import api
import logging

def mainScreen(online=True):
    user_cam = cv2.VideoCapture(0)

    if not user_cam.isOpened():
        logging.error("Failed to open camera")
        return

    detector = pm.poseDetector()

    while user_cam.isOpened():
        ret_val, image_1 = user_cam.read()
        if not ret_val:
            continue

        image_1 = detector.findPose(image_1)
        handList_user = detector.findHand(image_1)
        person_detected = handList_user is not None and len(handList_user) >= 2

        if online and person_detected:
            try:
                value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]
                api.gamedata_api("/HandData/1", "PUT", value)
            except Exception as e:
                logging.error("An error occurred: %s", e)
        elif online and not person_detected:
            cv2.putText(image_1, "No person detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        ret_val, buffer = cv2.imencode('.jpg', image_1)
        if not ret_val:
            logging.error("Failed to encode frame")
            continue

        image_1 = buffer.tobytes()

        yield (b'--image\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + image_1 + b'\r\n')

    user_cam.release()