SQLite 프롬프트에 입력해 테이블 생성

docker exec -it robot-control bash

sqlite3 robot.db

CREATE TABLE pinky_status (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  robot_id TEXT,
  status TEXT,
  emergency INTEGER DEFAULT 0,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pinky_command (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  robot_id TEXT,
  command TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

.exit

 

docker restart robot-control

 

app.py에 명령 API 추가

pinky1 명령 저장

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

pinky1 최근 명령 조회

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

 

Pinky(모바일로봇) 연동 준비

curl -X POST -H "Content-Type: application/json" \
  -d '{"robot_id":"T1_pinky1", "status":"moving", "emergency":0}' \
  <http://<서버_IP>>:5000/pinky1/status

 

Pinky 구동 명령 내리기


server_T1_P1_test_0707.txt
08 Jul 2025, 10:00 AM
curl -X POST -H "Content-Type: application/json" \
  -d '{"robot_id":"T1_pinky1", "command":"go_to_A"}' \
  http://localhost:5000/pinky1/command

 

여러 데이터 한 번에 쭉 출력하는 API 만들기

: 서버 코드(app.py)에서 여러 건 조회 API 추가

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

→  /pinky1/status/all로 접속하면 최근 20건이 한 번에 JSON으로 나옵니다.

 

연결이 되지 않을 때 확인할 점

docker ps : 서버 IP / PORT 확인.
PORTS 항목이 0.0.0.0:5000->5000/tcp처럼 되어 있어야 외부에서 접근 가능.

docker logs robot-control : 서버가 제대로 실행중인지 확인
서버에서 IP 확인하기 : hostname -I

curl http://localhost:5000/pinky1/status
curl http://<서버의_실제_IP>:5000/pinky1/status

Pinky 에서 ping 테스트 : ping <서버의_실제_IP>

Docker 컨테이너 실행 옵션 확인 : 컨테이너 실행 시 반드시 -p 5000:5000 옵션을 줘야 외부에서 접근 가능docker run -d -p 5000:5000 --name robot-control robot-control

서버 IP가 192.168.0.28이라면, 핑키에서 아래처럼 요청해야 합니다.
curl -X POST -H "Content-Type: application/json" \   -d '{"robot_id":"T1_pinky1", "status":"moving", "emergency":0}' \   http://192.168.0.28:5000/pinky1/status
