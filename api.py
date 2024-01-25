import requests
import json

def gamedata_api(path, method, variable):
    # 로컬 테스트 용 주소와 실제 클라우드 주소
    # API_HOST = "http://127.0.0.1:8080/api"
    API_HOST = "http://175.106.97.249:8080/api"

    # POST와 PUT 전용 전달될 자료
    value = variable

    # 데이터 베이스에 있는 테이블과 컬럼 이름
    body = None

    headers = {
        "Content-Type": "application/json", "charset": "UTF-8", "Accept": "*/*"
    }

    if path == "/AccuracyData":
        gameBody = {
            "znickname": value[0],
            "capture_time": value[1],
            "accuracy": value[2]
        }
        body = gameBody

    elif path == "/BackgroundData":
        backgroundBody = {
            "znickname": value,
            "is_vr": 0,
            "bg_name": "",
            "coord_name": ""
        }
        body = backgroundBody

    elif path == "/BasicData":
        basicBody = {
            "znickname": value[0],
            "reaction_time": value[1],
            "on_air": value[2],
            "squat_jump": value[3],
            "knee_punch": value[4],
            "balance_test": value[5],
            "basic_rating": value[6]
        }
        body = basicBody

    elif path == "/HandData":
        handBody = {
            "znickname": value[0],
            "rx": value[1],
            "ry": value[2],
            "lx": value[3],
            "ly": value[4]
        }
        body = handBody

    elif path == "/HandData/1":
        handBody = {
            "znickname": value[0],
            "rx": value[1],
            "ry": value[2],
            "lx": value[3],
            "ly": value[4]
        }
        body = handBody

    elif path == "/PlayerData":
        playerBody = {
            "znickname": value[0],
            "total": value[1],
            "total_top": value[2],
            "total_bottom": value[3],
            "perfect_frame": value[4],
            "awesome_frame": value[5],
            "good_frame": value[6],
            "ok_frame": value[7],
            "bad_frame": value[8],
            "recommend_content": value[9]
        }
        body = playerBody

    elif path == "/ProgramData":
        programBody = {
            "znickname": value[0],
            "is_running": value[1]
        }
        body = programBody
    
    elif path == "/TwoPlayerData":
        twoPlayerBody = {
            "znickname": value[0],
            "capture_time": value[1],
            "first_player": value[2],
            "second_player": value[3]
        }
        body = twoPlayerBody

    elif path == "/TwoPlayerFinalData":
        twoPlayerFinalBody = {
            "znickname": value[0],
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

    # 주소와 해당 API의 이름
    url = API_HOST + path

    try:
        global response
        response = None
        
        # GET POST DELETE PUT Method를 지정해줍니다
        if method == "GET":
            response = requests.get(url, headers=headers)

            return response.text
        
        elif method == "POST":
            response = requests.post(url, headers=headers, json=body)

        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=body)

    except Exception as ex:
        print(ex)