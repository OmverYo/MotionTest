from flask import Flask, jsonify, render_template, Response, stream_with_context
import requests
import mainScreen, gameRun, basicRun, onAir, kneePunch, balanceTest, squatJump, twoPlayerEstimate, twoPlayerCam
import api

app = Flask(__name__)

@app.route('/check-status', methods=['GET'])
def check_status():
    try:
        response = requests.get('https://www.google.com/', timeout=3)
        if response.status_code == 200:
            return jsonify({'status': 'online'})
        else:
            return jsonify({'status': 'offline'})
    except requests.ConnectionError:
        return jsonify({'status': 'offline'})

@app.route('/start-game', methods=['GET'])
def start_game():
    status_response = check_status()
    status = status_response.get_json()['status']

    if status == 'online':
        return Response(stream_with_context(gameRun.online_mode()),
                        content_type='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response(stream_with_context(gameRun.offline_mode()),
                        content_type='multipart/x-mixed-replace; boundary=frame')


@app.route('/gameRun')
def game():
    return render_template('gameRun.html')

@app.route('/basicRun')
def basic():
    return render_template('basicRun.html')

@app.route('/onAir')
def air():
    return render_template('onAir.html')

@app.route('/kneePunch')
def knee():
    return render_template('kneePunch.html')

@app.route('/balanceTest')
def balance():
    return render_template('balanceTest.html')

@app.route('/squatJump')
def squat():
    return render_template('squatJump.html')

@app.route('/mainScreen')
def main():
    return render_template('mainScreen.html')

@app.route('/twoPlayer')
def two():
    twoPlayerEstimate.twoPlayer()

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

@app.route('/video_main')
def video_main():
    return Response(mainScreen.mainScreen(), mimetype='multipart/x-mixed-replace; boundary=image')

if __name__ == '__main__':
    app.run(debug=True)