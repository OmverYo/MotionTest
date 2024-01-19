from flask import Flask, render_template, Response
import mainScreen, gameRun, basicRun, onAir, kneePunch, balanceTest, squatJump, twoPlayerEstimate
import api

app = Flask(__name__)

@app.route('/gameRun')
def game():
    api.gamedata_api("/ProgramData", "DELETE", None)
    return render_template('gameRun.html')

@app.route('/basicRun')
def basic():
    api.gamedata_api("/ProgramData", "DELETE", None)
    return render_template('basicRun.html')

@app.route('/onAir')
def air():
    api.gamedata_api("/ProgramData", "DELETE", None)
    return render_template('onAir.html')

@app.route('/kneePunch')
def knee():
    api.gamedata_api("/ProgramData", "DELETE", None)
    return render_template('kneePunch.html')

@app.route('/balanceTest')
def balance():
    api.gamedata_api("/ProgramData", "DELETE", None)
    return render_template('balanceTest.html')

@app.route('/squatJump')
def squat():
    api.gamedata_api("/ProgramData", "DELETE", None)
    return render_template('squatJump.html')

@app.route('/mainScreen')
def main():
    api.gamedata_api("/ProgramData", "DELETE", None)
    return render_template('mainScreen.html')

@app.route('/twoPlayer')
def two():
    api.gamedata_api("/ProgramData", "DELETE", None)
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