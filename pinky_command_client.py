import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import requests
import time

SERVER_IP = "20.249.209.1"  # 서버의 실제 IP로 수정
ROBOT_ID = "T1_pinky1"

def get_command():
    url = f"http://{SERVER_IP}:5000/pinky1/command"
    try:
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if data["command"]:
                return data["command"][2]  # command 값
    except Exception as e:
        print("Error getting command:", e)
    return None

def report_status(status, emergency=0):
    url = f"http://{SERVER_IP}:5000/pinky1/status"
    payload = {
        "robot_id": ROBOT_ID,
        "status": status,
        "emergency": emergency
    }
    try:
        resp = requests.post(url, json=payload, timeout=2)
        print("Status reported:", resp.text)
    except Exception as e:
        print("Error reporting status:", e)

class PinkyCommandClient(Node):
    def __init__(self):
        super().__init__('pinky_command_client')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.last_command = None
        self.timer = self.create_timer(2.0, self.check_command)  # 2초마다 실행

    def check_command(self):
        command = get_command()
        if command and command != self.last_command:
            self.get_logger().info(f"New command received: {command}")
            if command == "go_to_A":
                self.move_to_A()
            elif command == "stop":
                self.stop_robot()
            elif command == "emergency_stop":
                self.stop_robot()
                report_status("emergency", emergency=1)
            else:
                self.get_logger().info(f"Unknown command: {command}")
            self.last_command = command

    def move_to_A(self):
        twist = Twist()
        twist.linear.x = 0.2  # 전진 속도 (예시)
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)
        report_status("moving")
        time.sleep(5)  # 이동 시뮬레이션 (실제 환경에 맞게 수정)
        twist.linear.x = 0.0
        self.cmd_pub.publish(twist)
        report_status("arrived")

    def stop_robot(self):
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)
        report_status("stopped")

def main(args=None):
    rclpy.init(args=args)
    node = PinkyCommandClient()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
