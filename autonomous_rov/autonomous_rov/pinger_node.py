#!/usr/bin/env python3

from brping import Ping1D
import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from rclpy.executors import MultiThreadedExecutor

class PingNode(Node):
    def __init__(self, ping):
        super().__init__('pinger_node')
        self.ping = ping
        self.data_pub = self.create_publisher(Float64MultiArray, '/ping/data', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10 Hz

    def timer_callback(self):
        data = self.ping.get_distance()
        if data:
            distance = data['distance']
            confidence = data['confidence']
            self.get_logger().info(f"Distance: {distance}\tConfidence: {confidence}%")
            msg = Float64MultiArray()
            msg.data = [float(distance), float(confidence)]
            self.data_pub.publish(msg)
        else:
            self.get_logger().warn("Failed to get distance data")

parser = argparse.ArgumentParser(description="Ping python library example.")
parser.add_argument('--device', action="store", required=False, type=str, help="Ping device port. E.g: /dev/ttyAMA3")
parser.add_argument('--baudrate', action="store", type=int, default=9600, help="Ping device baudrate. E.g: 115200")
parser.add_argument('--udp', action="store", required=False, type=str, help="Ping UDP server. E.g: 192.168.2.1:14550")
#parsed_args = parser.parse_args(args=args)
parsed_args, unknown = parser.parse_known_args()

if parsed_args.device is None and parsed_args.udp is None:
	parser.print_help()
	exit(1)

# Initialize the Ping
myPing = Ping1D()
if parsed_args.device is not None:
	myPing.connect_serial(parsed_args.device, parsed_args.baudrate)
elif parsed_args.udp is not None:
	host, port = parsed_args.udp.split(':')
	myPing.connect_udp(host, int(port))

if myPing.initialize() is False:
	print("Failed to initialize Ping!")
	exit(1)
myPing.set_speed_of_sound(343000)
speed_of_sound = myPing.get_speed_of_sound()
if speed_of_sound:
	print(f"Current speed of sound: {speed_of_sound['speed_of_sound']} mm/s")
else:
	print("Failed to retrieve speed of sound")
print("------------------------------------")
print("Starting Ping..")
print("Press CTRL+C to exit")
print("------------------------------------")
input("Press Enter to continue...")

#def main():
	#rclpy.init()
	#pinger_node = PingNode(myPing)
	#rclpy.spin(pinger_node)
	#pinger_node.destroy_node()
	#rclpy.shutdown()


def main():
    rclpy.init()
    pinger_node = PingNode(myPing)
    executor = MultiThreadedExecutor(num_threads=1)  # or another number
    executor.add_node(pinger_node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        pinger_node.destroy_node()
        rclpy.shutdown()



if __name__ == '__main__':
	main()

#     #192.168.2.2:9090
    #ros2 run ping_control ping_control --udp 192.168.2.2:9090
#     # ping 192.168.2.2 #blueos link address used in google search bar #9090 ping1D ID from blueos 
#used ping viewer app to know its address 
#     #PING 192.168.2.2 (192.168.2.2) 56(84) bytes of data.
#     # 64 bytes from 192.168.2.2: icmp_seq=1 ttl=64 time=13.4 ms
#     # 64 bytes from 192.168.2.2: icmp_seq=2 ttl=64 time=4.87 ms
#     # 64 bytes from 192.168.2.2: icmp_seq=3 ttl=64 time=3.98 ms

#     # nc -zv 192.168.2.2 9090
#     #Connection to 192.168.2.2 9090 port [tcp/*] succeeded!
#/opt/ros/humble/share/std_msgs/msg

