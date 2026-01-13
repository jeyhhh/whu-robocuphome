import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import math
import sys
#使用ros2控制机器人移动
class MoveNode(Node):
    def __init__(self):
        super().__init__('move_node')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('MoveNode has been started.')
        self.destination = {'x':0.0,'y':0.0} 

    def move(self,linear_x,angular_z,duration):
        msg = Twist()
        msg.linear.x = linear_x
        #msg.linear.y = lateral_y
        msg.angular.z = angular_z
        self.get_logger().info(f'Moving with linear_x: {linear_x}, angular_z: {angular_z} for duration: {duration}s')
        self.publish_move(msg,duration)

    def publish_move(self,msg,duration):#现在要定时为100hz频率发送
        end_time = time.time() + duration
        rate = rclpy.rate(100)  # 100 Hz
        while time.time() < end_time:
            self.publisher_.publish(msg)
            rate.sleep()

    def get_current_position(self):
        '''订阅odom话题获取当前机器人位置'''


    def position_to_move_straight(self,destination):
        '''只推荐当前机器人一整段不中途转弯的直线移动'''
        self.destination['x'] = destination['x']
        self.destination['y'] = destination['y']
        distance = math.sqrt(destination['x']**2 + destination['y']**2)
        angle = math.atan2(destination['y'], destination['x'])
        self.get_logger().info(f'Moving to position x: {destination["x"]}, y: {destination["y"]}, distance: {distance}, angle: {angle}')
        #先转向
        self.move(0.0,angle,abs(angle)/0.5) #假设转速为0.5rad/s
        #再直线前进
        self.move(0.2,0.0,distance/0.2) #假设线速度为0.2m/s
        #检查是否到达
        current_position = self.get_current_position()
        if (abs(current_position['x'] - destination['x']) < 0.05) and (abs(current_position['y'] - destination['y']) < 0.05):
            self.get_logger().info('Reached the destination successfully.')
        #这里需要实现订阅odom话题并返回当前坐标的逻辑
            self.stop()
        else:
            self.get_logger().info('Failed to reach the destination.')
            self.stop()

    def position_to_move_curve(self,destination):
        '''推荐当前机器人需要转弯的曲线移动'''
        

    def stop(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)
        self.get_logger().info('Robot stopped.')

    def destroy_node(self):
        self.stop()
        super().destroy_node()
    




