import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from rclpy.clock import Clock
import sys
import math

class InverseKinematicsPublisher(Node):

    def __init__(self):
        super().__init__('ik_node')
        topic_ = "/joint_states"
        self.joints = ['base_arm1_joint', 'arm1_arm2_joint', 'arm2_arm3_joint']

        # Robot arm link lengths (modify these according to your robot's specifications)
        self.L1 = 0.5  # Length of the first link
        self.L2 = 0.5  # Length of the second link
        self.L3 = 0.3  # Length of the third link

        # Handle command-line arguments
        if len(sys.argv) < 4:
            self.get_logger().error("Not enough arguments provided. Using default values.")
            self.goal_ = [0.5, 0.5, 0.5]  # Default end-effector position
        else:
            try:
                self.goal_ = [float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])]
            except ValueError:
                self.get_logger().error("Invalid argument(s) provided. Using default values.")
                self.goal_ = [0.5, 0.5, 0.5]  # Default end-effector position

        self.publisher_ = self.create_publisher(JointState, topic_, 10)
        self.timer_ = self.create_timer(0.1, self.timer_callback)

    def inverse_kinematics(self, x, y, z):
        # Calculate theta1 (base rotation)
        theta1 = math.atan2(y, x)

        # Distance from base to end-effector in the x-y plane
        r = math.sqrt(x**2 + y**2)

        # Distance from second joint to end-effector
        s = z - self.L1
        D = math.sqrt(r**2 + s**2)

        # Calculate theta3 using cosine law
        cos_theta3 = (D**2 - self.L2**2 - self.L3**2) / (2 * self.L2 * self.L3)
        if cos_theta3 > 1 or cos_theta3 < -1:
            self.get_logger().error("Target position is out of reach!")
            return None
        theta3 = math.acos(cos_theta3)

        # Calculate theta2
        theta2 = math.atan2(s, r) - math.atan2(self.L3 * math.sin(theta3), self.L2 + self.L3 * math.cos(theta3))

        return [theta1, theta2, theta3]

    def timer_callback(self):
        joint_angles = self.inverse_kinematics(self.goal_[0], self.goal_[1], self.goal_[2])
        if joint_angles is None:
            return
        msg = JointState()
        current_time = self.get_clock().now().to_msg()
        msg.header.stamp = current_time
        msg.name = self.joints
        msg.position = joint_angles
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing joint angles: {joint_angles}")

def main(args=None):
    rclpy.init(args=args)
    node = InverseKinematicsPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
