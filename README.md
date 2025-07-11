** 서버 호스트 IP : 192.168.0.28 기준으로 작성했습니다.
** pinky@192.168.0.216 을 이용하였습니다.

<< Server 구축을 위한 간단한 설명 >>
  서버: 로봇/팔/카메라의 상태를 받고, 명령을 내리고, DB에 기록하는 역할 (app.py)
  DB(SQLite): 모든 상태와 이력 데이터를 저장 (robot.db)
  Docker: 서버와 DB를 컨테이너로 관리해 쉽게 실행/중지/배포 (Dockerfile)
  * 3개의 파일이 모두 호스트의 같은 폴더 (ex. robot_control) 안에 있어야 함.



* 실행 단계:
    1. (pinky) pinky bringup 실행 (ing)
    2. (pinky) 로봇 명령 python 파일 실행 (ing)
    3. (HOST) 로봇 상태 서버로 보내기 (1회)
    4. (HOST) 서버에서 로봇 명령 내리기
    5. (WEB) http://192.168.0.28:5000/pinky1/status/all 확인 가능

1. ros2 launch pinky_bringup bringup.launch.xml

2. python3 /home/pinky/jeong/pinky_command_client.py

3. curl -X POST -H "Content-Type: application/json" \
  -d '{"robot_id":"T1_pinky1", "status":"moving", "emergency":0}' \
  http://<서버_IP>:5000/pinky1/status

4-1. 앞으로 전진
  curl -X POST -H "Content-Type: application/json" \
  -d '{"robot_id":"T1_pinky1", "command":"go_to_A"}' \
  http://<서버_IP>:5000/pinky1/command

4-2. 정지
   curl -X POST -H "Content-Type: application/json" \
  -d '{"robot_id":"T1_pinky1", "command":"go_to_A"}' \
  http://<서버_IP>:5000/pinky1/command

5-1. pinky 상태 1회 확인 (ex. moving/arrived/stopped)
   http://192.168.0.28:5000/pinky1/status

5-2. pinky 명령 확인 (ex. go_to_A/stop)
   http://192.168.0.28:5000/pinky1/command

5-3. pinky 상태 최근 20회 누적 확인
   http://192.168.0.28:5000/pinky1/status/all


<< 서버 구축 과정 >>
1. 서버 코드 작성 (app.py 파일)
2. DB 파일 생성 (sqlite3 robot.db)
3. 테이블 생성 (SQLite 프롬프트에서 아래 내용 입력)
4. Dockerfile 파일 생성 (Dockerfile 파일)
5. Docker 이미지 빌드 및 컨테이너 실행
  docker build -t robot-control .
  docker run -d -p 5000:5000 --name robot-control robot-control



<< Docker 사용 관련 내용 >>

** docker robot-control 을 이용하였습니다.
1f9ab088b270   robot-control   "python app.py"   14 minutes ago   Up 14 minutes   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   robot-control

* docker 실행:
  -> docker build -t robot-control .
    근데 실행할 때 docker를 뭔가를 해야하는지는 잘 모르겠습니다.
    실제로 이후 명령 작성 및 실행 등은 pinky/HOST 터미널만 사용하고, 굳이 docker에 접속하진 않았습니다.
    다음 과정에서, server DB를 받아오는 테이블을 생성하는 과정에서 docker를 이용했습니다.

* Dockerfile 파일 생성 후 아래 내용 입력:
  FROM python:3.11
  WORKDIR /app
  COPY . /app
  RUN pip install flask
  CMD ["python", "app.py"]

* 컨테이너에 sqlite3 설치하기
  docker exec -it robot-control bash
  apt-get update
  apt-get install sqlite3

* 마운트 한 DB 파일을 호스트에서 sqlite3 설치 후 조작하기
  sudo apt-get update
  sudo apt-get install sqlite3
  sqlite3 ./robot_control/robot.db

* SQLite 프롬프트에 입력해 테이블 생성
  1. docker exec -it robot-control bash
  2. sqlite3 robot.db

* 테이블 생성 명령 예시:
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

* app.py 코드 저장 후 도커 이미지 재빌드 & 컨테이너 재실행
    docker stop robot-control
    docker rm robot-control
    docker build -t robot-control .
    docker run -d -p 5000:5000 --name robot-control robot-control


* 연결이 되지 않을 때 확인할 점

- docker ps : 서버 IP / PORT 확인.
  PORTS 항목이 0.0.0.0:5000->5000/tcp처럼 되어 있어야 외부에서 접근 가능.
- docker logs robot-control : 서버가 제대로 실행중인지 확인
  서버에서 IP 확인하기 : hostname -I
  curl http://localhost:5000/pinky1/status
  curl http://<서버의_실제_IP>:5000/pinky1/status 
- Pinky 에서 ping 테스트 : ping <서버의_실제_IP>
- Docker 컨테이너 실행 옵션 확인:
  컨테이너 실행 시 반드시 -p 5000:5000 옵션을 줘야 외부에서 접근 가능docker run -d -p 5000:5000 --name robot-control robot-control
- 서버 IP가 192.168.0.28이라면, 핑키에서 아래처럼 요청해야 합니다.
curl -X POST -H "Content-Type: application/json" \   -d '{"robot_id":"T1_pinky1", "status":"moving", "emergency":0}' \   http://192.168.0.28:5000/pinky1/status
