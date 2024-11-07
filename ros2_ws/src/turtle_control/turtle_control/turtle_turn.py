import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math

# Defining the TurtleControllerNode class that inherits from Node
class TurtleControllerNode(Node):
    # Constructor method for the class
    def __init__(self):
        # Calling the parent class constructor and naming the node "turtle_controller"
        super().__init__("turtle_turn")

        # Setting target coordinates for the turtle
        self.target_x = 9.0
        self.target_y = 4.0

        # Initializing the pose variable
        self.pose_ = None

        # Creating a publisher for the cmd_vel topic to send velocity commands to the turtle
        self.cmd_vel_publisher_ = self.create_publisher(Twist, "turtle1/cmd_vel", 10)
        # Creating a subscriber for the pose topic to get the turtle's current pose
        self.pose_subscriber_ = self.create_subscription(Pose, "turtle1/pose", self.callback_turtle_pose, 10)

        # Creating a timer to call the control loop periodically (every 0.01 seconds)
        self.control_loop_timer_ = self.create_timer(0.01, self.control_loop)
        # Callback function to update the pose of the turtle

    def callback_turtle_pose(self, msg):
        self.pose_ = msg
        # Control loop function to send velocity commands to the turtle

    def control_loop(self):
        # If the pose is not yet received, do nothing.
        if self.pose_ is None:
            return
        
        # Calculate the distance between the current pose and the target
        dist_x = self.target_x - self.pose_.x
        dist_y = self.target_y - self.pose_.y
        distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)

        # Create a Twist message to send velocity commands
        msg = Twist()

        # If the distance is greater than a threshold, set linear and angular velocities
        if distance > 0.5:
            msg.linear.x = distance

            # Calculate the angle to the goal
            goal_theta = math.atan2(dist_y, dist_x)
            diff = goal_theta - self.pose_.theta

            # Normalize the angle difference
            if diff > math.pi:
                diff -= 2 * math.pi
            elif diff < -math.pi:
                diff += 2 * math.pi

            msg.angular.z = diff

        else:
            # If the turtle is close enough to the target, stop the turtle
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        # Publish the velocity command
        self.cmd_vel_publisher_.publish(msg)

        # Callback function for the move_location service
    def callback_get_distance(self, request, response):

        # Calculate the distance to the requested location
        x = request.loc_x - self.pose_.x
        y = request.loc_y - self.pose_.y
        response.distance = math.sqrt(x * x + y * y)

        return response
    
# Main function to initialize and spin the ROS2 node
def main(args=None):
    # Initialize the rclpy library
    rclpy.init(args=args)
    # Create an instance of the TurtleControllerNode
    node = TurtleControllerNode()
    # Spin the node so its callbacks are called
    rclpy.spin(node)
    # Shutdown the rclpy library
    rclpy.shutdown()

# Entry point of the script
if __name__ == "__main__":
    main()