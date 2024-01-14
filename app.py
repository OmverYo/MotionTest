from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import poseModule as pm

mp_pose = mp.solutions.pose
mp_selfie_segmentation = mp.solutions.selfie_segmentation
segment = mp_selfie_segmentation.SelfieSegmentation

app = Flask(__name__)

camera = cv2.VideoCapture(0)

def openMain():

    detector = pm.poseDetector()

    with mp_selfie_segmentation.SelfieSegmentation(model_selection = 0) as selfie_segmentation, mp_pose.Pose(model_complexity = 0, min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose:
        # 배경화면의 색상을 지정합니다
        BG_COLOR = (0, 255, 0) # GREEN

        bg_image = None
        
        success, image = camera.read()

        image = detector.findPose(image)
        results1 = detector.findHand(image)

        results = selfie_segmentation.process(image)

        condition = np.stack((results.segmentation_mask,) * 3, axis = -1) > 0.15

        # 만약 지정된 배경화면이 없을 경우
        if bg_image is None:
            bg_image = np.zeros(image.shape, dtype = np.uint8)
            bg_image[:] = BG_COLOR
        
        # 결과 이미지를 적용합니다
        output_image = np.where(condition, image, bg_image)

        return results1

        # ret, buffer = cv2.imencode('.jpg', output_image)
        # output_image = buffer.tobytes()
        # yield (b'--image\r\n'
        #     b'Content-Type: image/jpeg\r\n\r\n' + output_image + b'\r\n')

@app.route('/main', methods=['GET'])
def main():
    return openMain()

# @app.route('/main')
# def main():
#     return render_template('main.html')

# @app.route('/video_main')
# def video_main():
#     return Response(openMain(), mimetype='multipart/x-mixed-replace; boundary=image')

if __name__ == '__main__':
    app.run(debug=True)