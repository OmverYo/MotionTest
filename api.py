import requests
import json

def gamedata_api(path, method, variable):
    API_HOST = "http://127.0.0.1:8080/api"

    value = variable

    body = None

    headers = {
        "Content-Type": "application/json", "charset": "UTF-8", "Accept": "*/*"
    }

    if path == "/BackgroundData":
        backgroundBody = {
            "is_vr": 1,
            "bg_name": "",
            "coord_name": ""
        }
        body = backgroundBody

    elif path == "/BasicData":
        basicBody = {
            "reaction_time": value[0],
            "on_air": value[1],
            "squat_jump": value[2],
            "knee_punch": value[3],
            "balance_test": value[4],
            "basic_rating": value[5]
        }
        body = basicBody

    elif path == "/HandData":
        handBody = {
            "rx": value[0],
            "ry": value[1],
            "lx": value[2],
            "ly": value[3]
        }

        body = handBody

    elif path == "/HandData/1":
        handBody = {
            "hand_id": 1,
            "rx": value[0],
            "ry": value[1],
            "lx": value[2],
            "ly": value[3]
        }
        body = handBody

    elif path == "/AccuracyData":
        gameBody = {
            "capture_time": value[0],
            "accuracy": value[1]
        }
        body = gameBody

    elif path == "/PlayerData":
        playerBody = {
            "total": value[0],
            "total_top": value[1],
            "total_bottom": value[2],
            "perfect_frame": value[3],
            "awesome_frame": value[4],
            "good_frame": value[5],
            "ok_frame": value[6],
            "bad_frame": value[7],
            "recommend_content": value[8]
        }
        body = playerBody

    elif path == "/ProgramData":
        programBody = {
            "is_running": value
        }
        body = programBody
    
    elif path == "/TwoPlayerData":
        twoPlayerBody = {
            "capture_time": value[0],
            "first_player": value[1],
            "second_player": value[2]
        }
        body = twoPlayerBody

    elif path == "/TwoPlayerFinalData":
        twoPlayerFinalBody = {
            "total_first": value[1],
            "perfect_frame_first": value[2],
            "awesome_frame_first": value[3],
            "good_frame_first": value[4],
            "ok_frame_first": value[5],
            "bad_frame_first": value[6],
            "total_second": value[7],
            "perfect_frame_second": value[8],
            "awesome_frame_second": value[9],
            "good_frame_second": value[10],
            "ok_frame_second": value[11],
            "bad_frame_second": value[12]
        }
        body = twoPlayerFinalBody

    url = API_HOST + path

    try:
        global response
        response = None
        
        if method == "GET":
            response = requests.get(url, headers=headers)

            return response.text
        
        elif method == "POST":
            response = requests.post(url, headers=headers, json=body)

            # return True

        elif method == "DELETE":
            response = requests.delete(url, headers=headers)

            # return True
        
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=body)

            # return True

    except Exception as ex:
        print(ex)