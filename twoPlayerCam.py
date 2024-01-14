import cv2
import poseModule as pm
import api
import pathlib

def twoPlayerCam():
    try:
        path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"

        user_cam = cv2.VideoCapture(0)
        
        detector = pm.poseDetector()

        while user_cam.isOpened():
            try:
                success, image = user_cam.read()

                image = detector.findPose(image)
                handList_user = detector.findHand(image)

                value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]

                api.gamedata_api("/HandData", "POST", value)

                success, image = user_cam.read()

                ret, buffer = cv2.imencode('.jpg', output_image)
                
                output_image = buffer.tobytes()

                yield (b'--image\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + output_image + b'\r\n')
                    
            except:
                success, image = user_cam.read()

                ret, buffer = cv2.imencode('.jpg', output_image)
                
                output_image = buffer.tobytes()

                yield (b'--image\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + output_image + b'\r\n')
        
        user_cam.release()
    
    except:
        success, image = user_cam.read()

        while user_cam.isOpened():
            ret, buffer = cv2.imencode('.jpg', output_image)
            
            output_image = buffer.tobytes()

            yield (b'--image\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + output_image + b'\r\n')
            
        user_cam.release()