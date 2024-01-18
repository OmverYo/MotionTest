# import api

# result = api.gamedata_api("/PlayerData", "GET", None)
# print("Ok")

# # import api
# # import json
# # import logging

# # value = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# # try:
# #     result = api.gamedata_api("/PlayerData", "POST", value)

# #     if result == None:
# #         print("None")
    
# #     else:
# #         print("Ok")

# # except Exception as e:
# #     logging.error("An error occurred: %s", e)

# # try:
# #     result = api.gamedata_api("/BackgroundData", "GET", None)

# #     data = json.loads(result)

# #     print(data)
    
# #     myVR = data["is_vr"]
# #     bg_name = data["bg_name"]
# #     coord_name = data["coord_name"]

# #     if result == None:
# #         print("None")
    
# #     else:
# #         print(myVR)
# #         print(bg_name)
# #         print(coord_name)

# # except Exception as e:
# #     logging.error("An error occurred: %s", e)

# # import json
# # import pathlib

# # path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"

# # with open(f"{path}coordinates/TK_Motion01_C_FV_m_C0553.mp4.json") as json_file:
# #     json_data = json.load(json_file)

# import cv2
# import time
# import numpy as np

# cam = cv2.VideoCapture(0)

# start = time.time()

# while True:
#     success, usercam = cam.read()
#     end = time.time()
#     if end - start >= 5:
#         break
#     userflip = cv2.flip(usercam, 1)
#     cv2.imshow('frame', userflip)
#     print("Ok1")
#     if cv2.waitKey(1) == ord('q'):
#         break

# while True:
#     success, usercam = cam.read()
#     end = time.time()
#     userflip = cv2.flip(usercam, 1)
#     cv2.imshow('frame', userflip)
#     print("Ok2")
#     if cv2.waitKey(1) == ord('q'):
#         break

# cam.release()
# cv2.destroyAllWindows()

# # import numpy as np
# # import cv2 as cv
# # cap = cv.VideoCapture(0)
# # if not cap.isOpened():
# #     print("Cannot open camera")
# #     exit()
# # while True:
# #     # Capture frame-by-frame
# #     ret, frame = cap.read()
# #     # if frame is read correctly ret is True
# #     if not ret:
# #         print("Can't receive frame (stream end?). Exiting ...")
# #         break
# #     # Our operations on the frame come here
# #     gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
# #     # Display the resulting frame
# #     cv.imshow('frame', gray)
# #     if cv.waitKey(1) == ord('q'):
# #         break
# # # When everything done, release the capture
# # cap.release()
# # cv.destroyAllWindows()