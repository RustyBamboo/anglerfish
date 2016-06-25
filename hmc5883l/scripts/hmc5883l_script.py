#!/usr/bin/python

import sys
import smbus
import time
import math
import rospy
from std_msgs.msg import Float64, Float32
from std_msgs.msg import Header
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import MagneticField
from hmc5883l.msg import mag_raw

class measure_headings():

	def read_byte(self, adr):
	    return self.bus.read_byte_data(self.HMC5883L_ADDR, adr)

	def read_word(self, adr):
	    high = self.bus.read_byte_data(self.HMC5883L_ADDR, adr)
	    low = self.bus.read_byte_data(self.HMC5883L_ADDR, adr+1)
	    val = (high << 8) + low
	    return val
	    
	def read_word_2c(self, adr):
	    val = self.read_word(adr)
	    if (val >= 0x8000):
	        return -((65535 - val) + 1)
	    else:
	        return val

	def write_byte(self, adr, value):
	    self.bus.write_byte_data(self.HMC5883L_ADDR, adr, value)

	def get_reading(self): 
	        self.x_out = (self.read_word_2c(3) * self.scale)/10000  #10000 for Gauss to Tesla conversion
	        self.y_out = (self.read_word_2c(7) * self.scale)/10000
	        self.z_out = (self.read_word_2c(5) * self.scale)/10000

	        self.roll  = math.atan2(self.y_out, self.z_out) 
	        if (self.roll < 0):
	            self.roll += 2 * math.pi

	        self.pitch  = math.atan2(self.x_out, self.z_out) 
	        if (self.pitch < 0):
	           self.pitch += 2 * math.pi

	        self.yaw  = math.atan2(self.y_out, self.x_out) 
	        if (self.yaw < 0):
	           self.yaw += 2 * math.pi

        #print self.x_out

	def __init__(self):
	    self.bus = smbus.SMBus(1)

	    self.HMC5883L_ADDR       = 0x1E  #HMC5883L address

	    self.mag_pub = rospy.Publisher("/imu/mag_raw", MagneticField, queue_size=1)
	    self.rpy_pub = rospy.Publisher("/mag_raw_rpy", mag_raw, queue_size=1)

	    self.write_byte(0x00, 0b01111000) # Set to 8 samples @ 75Hz
	    self.write_byte(0x01, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
	    self.write_byte(0x02, 0b00000000) # Continuous sampling

	    self.scale = 0.92

	    self.x_offset = 47
            self.y_offset = -67
            self.z_offset = -73

            self.roll = 0.0
            self.pitch = 0.0
            self.yaw = 0.0

            rpy = mag_raw()

            rate = rospy.Rate(75) #Hz

            while not rospy.is_shutdown():
                self.get_reading()
                #print self.x_out

                mag = MagneticField(
                header = Header(
                    stamp = rospy.get_rostime(),
                    frame_id = 'magnetometer_raw'
                ),
                magnetic_field = Vector3(self.x_out, self.y_out, self.z_out)#,
                # magnetic_field_covariance = [ 2.19918421e+01, 6.13875066e-01, 3.68221974e-01,
                #     0, 2.17394286e+01, -5.56954205e-03, 
                #     0, 0, 2.41408444e+01]
                )

                rpy.header = Header(
                    stamp = rospy.get_rostime(),
                    frame_id = 'mag_raw_rpy'
                )
                rpy.roll = self.roll
                rpy.pitch = self.pitch
                rpy.yaw = self.yaw

                #print mag.header	
                self.mag_pub.publish(mag)
		self.rpy_pub.publish(rpy)
                rate.sleep()

def main(args):
	rospy.init_node('hmc5883l_magnetometer', anonymous=False)

	measure_headings()

        try:
		rospy.spin()
        except rospy.ROSInterruptException:
		print "Shutting down"
                pass
	


if __name__ == '__main__':
	main(sys.argv)
