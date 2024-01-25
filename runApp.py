from flask import Flask, render_template, Response
import mainScreen, gameRun, basicRun, onAir, kneePunch, balanceTest, squatJump, twoPlayerEstimate
import api
import pathlib
import json

# Flask를 불러와 기능을 app으로 지정
app = Flask(__name__)

# 해당 기능 또는 함수를 호출하기 위해 127.0.0.1:5000/ 다음 들어갈 주소
@app.route('/gameRun')
def game():
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]
    api.gamedata_api("/ProgramData", "POST", [nickname, 0])
    return render_template('gameRun.html')

@app.route('/basicRun')
def basic():
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]
    api.gamedata_api("/ProgramData", "POST", [nickname, 0])
    return render_template('basicRun.html')

@app.route('/onAir')
def air():
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]
    api.gamedata_api("/ProgramData", "POST", [nickname, 0])
    return render_template('onAir.html')

@app.route('/kneePunch')
def knee():
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]
    api.gamedata_api("/ProgramData", "POST", [nickname, 0])
    return render_template('kneePunch.html')

@app.route('/balanceTest')
def balance():
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]
    api.gamedata_api("/ProgramData", "POST", [nickname, 0])
    return render_template('balanceTest.html')

@app.route('/squatJump')
def squat():
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]
    api.gamedata_api("/ProgramData", "POST", [nickname, 0])
    return render_template('squatJump.html')

@app.route('/mainScreen')
def main():
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]
    api.gamedata_api("/ProgramData", "POST", [nickname, 0])
    return render_template('mainScreen.html')

@app.route('/twoPlayer')
def two():
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]
    api.gamedata_api("/ProgramData", "POST", [nickname, 0])
    twoPlayerEstimate.twoPlayer()
    # return render_template('twoPlayer.html')

# 여기서 부턴 HTML의 영상 부분을 담당
@app.route('/video_feed')
def video_feed():
    return Response(gameRun.gameRun(), mimetype='multipart/x-mixed-replace; boundary=image')

@app.route('/video_basic')
def video_basic():
    return Response(basicRun.basicRun(), mimetype='multipart/x-mixed-replace; boundary=image')

@app.route('/video_air')
def video_air():
    return Response(onAir.air(), mimetype='multipart/x-mixed-replace; boundary=image')

@app.route('/video_kneePunch')
def video_kneePunch():
    return Response(kneePunch.kneePunch(), mimetype='multipart/x-mixed-replace; boundary=image')

@app.route('/video_balance')
def video_balance():
    return Response(balanceTest.balanceTest(), mimetype='multipart/x-mixed-replace; boundary=image')

@app.route('/video_squat')
def video_squat():
    return Response(squatJump.squatJump(), mimetype='multipart/x-mixed-replace; boundary=image')

# @app.route('/video_two')
# def video_two():
#     return Response(twoPlayerEstimate.twoPlayer(), mimetype='multipart/x-mixed-replace; boundary=image')

@app.route('/video_main')
def video_main():
    return Response(mainScreen.mainScreen(), mimetype='multipart/x-mixed-replace; boundary=image')

# 파일이 실행될때 첫 실행 구문
# batch file을 이용하여 파이썬을 외부 프로세스로 언리얼 엔진 밖에서 실행
if __name__ == '__main__':
    app.run(debug=True)