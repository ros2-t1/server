** 서버 호스트 IP : 192.168.0.28 기준으로 작성했습니다.
** pinky@192.168.0.216 을 이용하였습니다.

<< 팀원이 Docker 없이 접속하는 방법 >>
- 서버 측: Python, Flask, sqlite3 설치 → app.py 실행
- 로봇 측: ROS2 bringup, Python 명령 클라이언트 실행 (SERVER_IP 수정)
- 명령/상태 전송: curl 또는 Python 코드로 HTTP 요청
- 로그 확인: 웹 브라우저로 서버 API 접속
즉, Docker 없이도 Python과 Flask, sqlite3만 설치하면 동일하게 서버와 연동하여 로봇을 제어하고 로그를 받아볼 수 있습니다.
서버의 IP와 포트, DB 파일 위치만 정확히 맞추면 됩니다.

1. 서버 환경 준비
  * sudo apt update
  * sudo apt install python3 python3-pip sqlite3
  * pip3 install flask

2. 서버 실행
  * python3 app.py
    - 터미널에서 app.py 가 있는 디렉토리로 이동 후, 위 명령어로 서비스 실행

- 서버가 정상적으로 실행되면,
    http://<서버_IP>:5000/pinky1/status/all 등 API 엔드포인트에 접근할 수 있습니다.

3. 로봇 제어 클라이언트 파일 준비
    - 로봇 제어용 Python 파일(pinky_command_client.py)을 각 로봇 PC 또는 제어 PC에 복사합니다.
    - SERVER_IP를 실제 서버의 IP로 수정해야 합니다.
    - ROS2 환경이 준비되어 있어야 하며, 필요한 패키지(예: geometry_msgs)가 설치되어 있어야 합니다.

4. 로봇 bringup 및 명령 클라이언트 실행
    - ROS2 bringup 실행 : ros2 launch pinky_bringup bringup.launch.xml
    - 로봇 명령 클라이언트 실행 : python3 /home/pinky/jeong/pinky_command_client.py

5. 로봇 명령 전송
- 상태 전송:
  * curl -X POST -H "Content-Type: application/json" \ -d '{"robot_id":"T1_pinky1", "status":"moving", "emergency":0}' \ http://<서버_IP>:5000/pinky1/status
- 명령 전송:
  * curl -X POST -H "Content-Type: application/json" \ -d '{"robot_id":"T1_pinky1", "command":"go_to_A"}' \ http://<서버_IP>:5000/pinky1/command

- 웹에서 로그 확인
    - 웹 브라우저에서 http://<서버_IP>:5000/pinky1/status/all 주소로 접속하면, 최근 상태 로그를 확인할 수 있습니다.
    - 마지막 명령 확인 : ~/pinky1/command , 마지막 상태 확인 : ~/pinky1/status
- 참고 : 운영 환경에서 Flask 를 배포하는 예시
    * pip install gunicorn
    * gunicorn -w 4 -b 0.0.0.0:5000 app:app

** 문제 발생 시 해결법
1. Flask 서버 실행 시 "Address already in use" 에러 해결법
2. 현재 사용 중인 프로세스 찾기 -> lsof -i :5000
3. 해당 프로세스 종료하기 -> kill <찾은 PID> (ex. kill 12345)
4. 만약 바로 종료되지 않으면 강제로 종료하기 : ex. kill -9 12345
5. lsof 명령어로 찾지 못하는 경우:
  * ss -ltnp | grep 5000
  * sudo fuser -v -n tcp 5000
