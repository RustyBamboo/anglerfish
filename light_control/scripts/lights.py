#!/usr/bin/python

#import RPi.GPIO as GPIO
import pigpio
import time
import rospy
from std_msgs.msg import Bool, String

class start_lights():

	def green(self, power):
	    if power.data == 1:
		#self.pig.write(16, 1)
		self.green_flag = 1
	    else:
		#self.pig.write(16, 0)
		self.green_flag = 0

	def white(self, power):
	    if power.data == 1:
	        self.pig.write(12, 1)
	    else:
	        self.pig.write(12, 0)

	def lights_off():
		pi1 = pigpio.pi()
		pi1.write(12, 0)
		pi1.write(16, 0)		
		pi1.stop()

	def __init__(self):
		rospy.Subscriber('Green_led', Bool, self.green)
		rospy.Subscriber('White_led', Bool, self.white)
		#self.green_pub = rospy.Publisher("green_light", String, queue_size=1)
		#self.white_pub = rospy.Publisher("white_light", String, queue_size=1)

		self.pig = pigpio.pi()
		self.pig.set_mode(12, pigpio.OUTPUT)
		self.pig.set_mode(16, pigpio.OUTPUT)
		self.green_flag = 0

		rate = rospy.Rate(360) #Hz

		counter = 0

		while not rospy.is_shutdown():
			if self.green_flag == 0:
				self.pig.write(16, 0)
			elif self.green_flag == 1:
				if counter == 0 or counter == 1 or counter == 2 or counter == 3 or counter == 4 or counter == 5 or counter == 6 or counter == 7:  
					self.pig.write(16, 1)
				else:
					self.pig.write(16, 1) #self.pig.write(16, 0)
			counter += 1

			if counter > 23:
				#this resets the counter
				counter = 0
			rate.sleep()	

    	rospy.on_shutdown(lights_off)

if __name__ == '__main__':
        rospy.init_node('LED_control', anonymous=False)

        start_lights()

        try:
                rospy.spin()
        except rospy.ROSInterruptException:
                print "Shutting down"
                pass


