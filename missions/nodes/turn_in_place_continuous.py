#!/usr/bin/python

import rospy
import math
import geometry_msgs.msg 
from geometry_msgs.msg import Point, PoseWithCovarianceStamped
from sensor_msgs.msg import Joy
import tf, tf2_ros
from nav_msgs.msg import Odometry
from anglerfish_joy.msg import rpy, move

class mission(object):

	def __init__(self):

		mission_counter = 0
		counter = 0
		time_per_move = 40

		self.roll = 0
		self.pitch = 0
		self.yaw = 0
		self.X = 0
		self.Y = 0
		self.Z = 0


		self.orientation = rospy.Publisher("/rpy", rpy, queue_size = 1)
		self.position = rospy.Publisher("/move_rov", move, queue_size = 1)
		
		rate = rospy.Rate(10)

		while not rospy.is_shutdown():

			if mission_counter == 0 and self.yaw < math.pi:
				self.yaw += 0.01745
				self.Z = -1.0
				counter += 1
				if self.yaw >= math.pi:			
					self.yaw = -math.pi		
					mission_counter = 1
			elif mission_counter == 1 and self.yaw < 0:
				self.yaw += 0.01745
				if self.yaw >= 0.0:
					mission_counter = 2
					rospy.signal_shutdown("mission complete")						

			o = rpy()  #Roll pitch Yaw (orientation)
			p = move() #positional movement

			o.header.stamp = rospy.Time.now()
			o.header.frame_id = 'desired_orientation' # i.e. '/odom'

			o.Roll = self.roll
			o.Pitch = self.pitch
			o.Yaw = self.yaw

			p.header.stamp = rospy.Time.now()
			p.header.frame_id = 'desired_position' # i.e. '/odom'

			p.X = self.X
			p.Y = self.Y
			p.Z = self.Z

			self.orientation.publish(o)
			self.position.publish(p)

			rate.sleep()

def main():
	rospy.init_node('mission', anonymous=False)

	mission()

	try:
		rospy.spin()
	except rospy.ROSInterruptException:
		print "Shutting down"
		pass


if __name__ == '__main__':
	main() #sys.argv
