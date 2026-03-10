import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import time
import math
import sys
#使用ros2控制机器人移动
class MoveNode(Node):
    def __init__(self):
        super().__init__('move_node')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('MoveNode has been started.')

        self.destination = {'x':0.0,'y':0.0} # 目标位置
        
        self.current_position = {'x': 0.0, 'y': 0.0, 'yaw': 0.0}# 存储当前位姿（由 odom_callback 更新）

        self.odom_subscription = self.create_subscription(
            Odometry,
            'odom',
            self.odom_callback,
            10)
        self._subscriptions = []#存储所有的订阅者，防止被垃圾回收
        self._subscriptions.append(self.odom_subscription)

    def move(self,linear_x,angular_z,duration):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.publish_move(msg,duration)
        self.get_logger().info(f'Moving with linear_x: {linear_x}, angular_z: {angular_z} for duration: {duration}s')    

    def publish_move(self,msg,duration):#现在要定时为10hz频率发送
        #end_time = time.time() + duration
        start_time = self.get_clock().now()
        end_time = start_time + rclpy.time.Duration(seconds=duration)
        self.get_logger().info('Publishing movement commands...')
        rate = self.create_rate(10)  # 10 Hz
        #while time.time() < end_time:
        while rclpy.ok() and self.get_clock().now() < end_time:
            self.publisher_.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.05)  # 20Hz

    def odom_callback(self, msg: Odometry):
        """odom 话题回调，更新当前位姿（x, y, yaw）"""
        p = msg.pose.pose.position
        o = msg.pose.pose.orientation
        x = p.x
        y = p.y
        # 由四元数计算 yaw（绕 z 轴）
        siny_cosp = 2.0 * (o.w * o.z + o.x * o.y)
        cosy_cosp = 1.0 - 2.0 * (o.y * o.y + o.z * o.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        self.current_position['x'] = x
        self.current_position['y'] = y
        self.current_position['yaw'] = yaw

    def get_current_position(self):
        '''返回最新的位置信息字典：{'x':..., 'y':..., 'yaw':...}'''
        return dict(self.current_position)

    def position_to_move_straight(self,linear_speed=0.2, angular_speed=0.5):
        '''只推荐当前机器人一整段不中途转弯的直线移动'''
        origin_position = self.get_current_position()
        distance = math.sqrt((self.destination['x']-origin_position['x'])**2 + (self.destination['y']-origin_position['y'])**2)
        angle = math.atan2(self.destination['y']-origin_position['y'], self.destination['x']-origin_position['x'])
        self.get_logger().info(f'Moving to position x: {self.destination["x"]}, y: {self.destination["y"]}, distance: {distance}, angle: {angle}')


        #先转向
        self.move(0.0,angle,abs(angle)/angular_speed) #假设转速为angular_speed rad/s
        #再直线前进
        self.move(linear_speed,0.0,distance/linear_speed) #假设线速度为linear_speed m/s
        #检查是否到达
        current_position = self.get_current_position()
        if (abs(current_position['x'] - self.destination['x']) < 0.05) and (abs(current_position['y'] - self.destination['y']) < 0.05):
            self.get_logger().info('Reached the destination successfully.')
        #这里需要实现订阅odom话题并返回当前坐标的逻辑
            self.stop()
        else:
            self.get_logger().info('Failed to reach the destination.')
            self.stop()

    def position_to_move_curve(self,destination,linear_speed=0.2, angular_speed=0.5):
        '''推荐当前机器人需要转弯的曲线移动'''
        eps = 1e-5
        current_position = self.get_current_position()
        delta_x = self.destination['x'] - current_position['x']
        delta_y = self.destination['y'] - current_position['y']
        if abs(delta_x*math.sin(0) - delta_y*math.cos(0)) <= eps:
            self.get_logger().info('The path is nearly straight, using straight movement instead.')
            self.position_to_move_straight(linear_speed, angular_speed)
            return
        d = -(delta_x**2 + delta_y**2)/(2*(delta_x*math.sin(0) - delta_y*math.cos(0))) #计算曲率半径
        #没写完

    def stop(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)
        self.get_logger().info('Robot stopped.')

    def destroy_node(self):
        self.stop()
        super().destroy_node()
    

def main(args=None):
    '''测试用例'''
    rclpy.init(args=args)
    move_node = MoveNode()
    
    # Example usage
    #destination = {'x': 1.0, 'y': 1.0}  # Example destination
    #move_node.move(-0.2, 0.5, 5.0)  # Move forward for 5 seconds
    move_node.get_logger().info(str(move_node.get_current_position()))
    move_node.destination = {'x': 1.0, 'y': 0.0}
    move_node.position_to_move_straight()
    move_node.get_logger().info(str(move_node.get_current_position()))

if __name__ == '__main__':
    main()


