import api
import json
import logging

value = [1, 2, 3, 4, 5, 1]

try:
    result = api.gamedata_api("/BasicData", "POST", value)

    if result == None:
        print("None")
    
    else:
        print("Ok")

except Exception as e:
    logging.error("An error occurred: %s", e)

# try:
#     result = api.gamedata_api("/BackgroundData", "GET", None)

#     data = json.loads(result)

#     print(data)
    
#     myVR = data["is_vr"]
#     bg_name = data["bg_name"]
#     coord_name = data["coord_name"]

#     if result == None:
#         print("None")
    
#     else:
#         print(myVR)
#         print(bg_name)
#         print(coord_name)

# except Exception as e:
#     logging.error("An error occurred: %s", e)

# import json
# import pathlib

# path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"

# with open(f"{path}coordinates/TK_Motion01_C_FV_m_C0553.mp4.json") as json_file:
#     json_data = json.load(json_file)