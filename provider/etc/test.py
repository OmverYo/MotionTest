# import pathlib
# import json
# import api

# path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
# nickname = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

# with open(nickname) as nickname_file:
#     nickname_data = json.load(nickname_file)

# print(nickname_data["name"])

# # api.gamedata_api(f"/BackgroundData?nickname={nickname}", "GET", None)
# api.gamedata_api("/AccuracyData", "POST", [nickname, 5, 50])

import cv2

cap = cv2.VideoCapture(0)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while cap.isOpened():
    success, image = cap.read()

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()