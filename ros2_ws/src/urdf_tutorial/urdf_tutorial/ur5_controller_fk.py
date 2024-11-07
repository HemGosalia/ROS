import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from rclpy.clock import Clock
import sys
import atexit

class TrajectoryPublisher(Node):

    def __init__(self):
        super().__init__('trajectory_node')
        
        topic_ = "/joint_states"
        self.joints = [
            'shoulder_pan_joint', 'shoulder_lift_joint',  
            'elbow_joint', 'wrist_1_joint',  
            'wrist_2_joint', 'wrist_3_joint'
        ]

        # Handle command-line arguments
        if len(sys.argv) < 7:
            self.get_logger().error("Not enough arguments provided. Using default values.")
            self.goal_ = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Default values
        else:
            try:
                self.goal_ = [float(sys.argv[i]) for i in range(1, 7)]
            except ValueError:
                self.get_logger().error("Invalid argument(s) provided. Using default values.")
                self.goal_ = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Default values

        self.publisher_ = self.create_publisher(JointState, topic_, 10)
        self.timer_ = self.create_timer(0.1, self.timer_callback)

        # For interpolation
        self.current_position = [0.0] * len(self.joints)
        self.step_size = 0.01
        self.total_steps = int(1 / self.step_size)
        self.goal_reached = False

        # Register exit handler
        atexit.register(self.hold_final_position)

    def timer_callback(self):
        msg = JointState()
        current_time = Clock().now().to_msg()

        msg.header.stamp.sec = current_time.sec
        msg.header.stamp.nanosec = current_time.nanosec
        msg.name = self.joints

        if not self.goal_reached:
            # Interpolate each joint position towards the goal
            for i in range(len(self.joints)):
                self.current_position[i] += (self.goal_[i] - self.current_position[i]) * self.step_size

            # Check if the goal is reached
            if all(abs(self.goal_[i] - self.current_position[i]) < 0.01 for i in range(len(self.joints))):
                self.goal_reached = True
                self.get_logger().info("Goal reached. Holding position...")

        msg.position = self.current_position
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing position: {self.current_position}")

    def hold_final_position(self):
        msg = JointState()
        current_time = Clock().now().to_msg()

        msg.header.stamp.sec = current_time.sec
        msg.header.stamp.nanosec = current_time.nanosec
        msg.name = self.joints
        msg.position = self.current_position

        # Publish the final position one more time to ensure it's held
        self.publisher_.publish(msg)
        self.get_logger().info(f"Final position held: {self.current_position}")

def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
