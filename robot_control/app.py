from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

# pinky1 상태 저장
@app.route('/pinky1/status', methods=['POST'])
def update_status():
    data = request.json
    conn = sqlite3.connect('robot.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO pinky_status (robot_id, status, emergency) VALUES (?, ?, ?)",
        (data.get('robot_id', 'T1_pinky1'), data['status'], data.get('emergency', 0))
    )
    conn.commit()
    conn.close()
    return {'result': 'ok'}

# pinky1 상태 조회
@app.route('/pinky1/status', methods=['GET'])
def get_status():
    conn = sqlite3.connect('robot.db')
    c = conn.cursor()
    c.execute(
        "SELECT * FROM pinky_status WHERE robot_id=? ORDER BY updated_at DESC LIMIT 1",
        ('T1_pinky1',)
    )
    row = c.fetchone()
    conn.close()
    return {'data': row}

# pinky1 명령 저장
@app.route('/pinky1/command', methods=['POST'])
def send_command():
    data = request.json
    conn = sqlite3.connect('robot.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO pinky_command (robot_id, command) VALUES (?, ?)",
        (data.get('robot_id', 'T1_pinky1'), data['command'])
    )
    conn.commit()
    conn.close()
    return {'result': 'ok'}

# pinky1 최근 명령 조회
@app.route('/pinky1/command', methods=['GET'])
def get_command():
    conn = sqlite3.connect('robot.db')
    c = conn.cursor()
    c.execute(
        "SELECT * FROM pinky_command WHERE robot_id=? ORDER BY created_at DESC LIMIT 1",
        ('T1_pinky1',)
    )
    row = c.fetchone()
    conn.close()
    return {'command': row}

# 서버 코드(app.py)에서 여러 건 조회 API 추가
@app.route('/pinky1/status/all', methods=['GET'])
def get_all_status():
    conn = sqlite3.connect('robot.db')
    c = conn.cursor()
    c.execute(
        "SELECT * FROM pinky_status WHERE robot_id=? ORDER BY updated_at DESC LIMIT 20",
        ('T1_pinky1',)
    )
    rows = c.fetchall()
    conn.close()
    return {'data': rows}



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return render_template('status.html')

@app.route('/command')
def command():
    return render_template('command.html')


# pinky1 최근 명령 20개 조회
@app.route('/pinky1/command/all', methods=['GET'])
def get_all_commands():
    conn = sqlite3.connect('robot.db')
    c = conn.cursor()
    c.execute(
        "SELECT * FROM pinky_command WHERE robot_id=? ORDER BY created_at DESC LIMIT 20",
        ('T1_pinky1',)
    )
    rows = c.fetchall()
    conn.close()
    return {'data': rows}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




