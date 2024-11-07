#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import numpy as np

class InverseKinematicsPublisher(Node):

    def __init__(self):
        super().__init__('inverse_kinematics_node')
        topic_ = "/joint_trajectory_controller/joint_trajectory"
        self.joints = ['base_arm1_joint', 'arm1_arm2_joint', 'arm2_arm3_joint']
        self.link_lengths = [0.5, 0.5, 0.3]  # Length of arm1, arm2, and arm3
        self.joint_limits = [
            (-2.14, 2.14),  # base_arm1_joint limits
            (-2.14, 2.14),  # arm1_arm2_joint limits
            (-2.14, 2.14)   # arm2_arm3_joint limits
        ]
        self.declare_parameter("end_effector_pose", [0.5, 0.5, 0.5])
        self.goal_pose = self.get_parameter("end_effector_pose").value
        self.publisher_ = self.create_publisher(JointTrajectory, topic_, 10)
        self.timer_ = self.create_timer(1, self.timer_callback)

    def inverse_kinematics(self, x, y, z):
        L1, L2, L3 = self.link_lengths

        # Calculate the distance to the target
        target_distance = np.sqrt(x**2 + y**2 + z**2)

        # Check if the target is reachable
        if target_distance > sum(self.link_lengths):
            self.get_logger().warn("Target position is out of reach. Moving to closest possible position.")
            scale = sum(self.link_lengths) / target_distance
            x *= scale
            y *= scale
            z *= scale

        # Calculate theta1 (base rotation)
        theta1 = np.arctan2(y, x)

        # Calculate wrist center
        wc_x = x - L3 * np.cos(theta1)
        wc_y = y - L3 * np.sin(theta1)
        wc_z = z

        # Distance to wrist center
        D = np.sqrt(wc_x**2 + wc_y**2 + wc_z**2)

        # Calculate theta3
        cos_theta3 = (D**2 - L1**2 - L2**2) / (2 * L1 * L2)
        cos_theta3 = np.clip(cos_theta3, -1.0, 1.0)  # Ensure valid range
        theta3 = np.arccos(cos_theta3)

        # Calculate theta2
        theta2 = np.arctan2(wc_z, np.sqrt(wc_x**2 + wc_y**2)) - np.arctan2(L2 * np.sin(theta3), L1 + L2 * np.cos(theta3))

        # Apply joint limits
        theta1 = np.clip(theta1, self.joint_limits[0][0], self.joint_limits[0][1])
        theta2 = np.clip(theta2, self.joint_limits[1][0], self.joint_limits[1][1])
        theta3 = np.clip(theta3, self.joint_limits[2][0], self.joint_limits[2][1])

        return [theta1, theta2, theta3]

    def timer_callback(self):
        msg = JointTrajectory()
        msg.joint_names = self.joints
        point = JointTrajectoryPoint()
        joint_positions = self.inverse_kinematics(*self.goal_pose)
        point.positions = joint_positions
        point.time_from_start = Duration(sec=2)
        msg.points.append(point)
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing joint positions: {joint_positions}")

def main(args=None):
    rclpy.init(args=args)
    node = InverseKinematicsPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
