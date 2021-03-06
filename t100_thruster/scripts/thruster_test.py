#!/usr/bin/python

import sys
import time
from time import localtime,strftime
import datetime
import math
import rospy
import csv
from std_msgs.msg import Float32
from std_msgs.msg import Header
from std_msgs.msg import String
from t100_thruster.msg import t100_thruster_feedback
#from anglerfish.msg import t100_thruster_feedback
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import MagneticField
from orientation_estimater.msg import rpy_msg
from hmc5883l.msg import mag_raw
from mag_calibration.msg import mag_values

#RPY_raw: HMC5883L script
#RPY_compensated: mag_cal_script
#Tesla_raw: mag_cal_script
#Tesla_compensated: 


class start_test():

	def arm_thrusters(self):
		rospy.loginfo("Arming thrusters...")
		for i in range (0,10):
			self.thrust1_pub.publish(0.0)
			self.thrust2_pub.publish(0.0)
			self.thrust3_pub.publish(0.0)
			self.thrust4_pub.publish(0.0)
			self.thrust5_pub.publish(0.0)
			self.thrust6_pub.publish(0.0)
			self.rate.sleep()


	def forward(self):
		output = (float(self.counter)/self.resolution) * self.forward_thrust_force
		
		if output == 0:
			self.initial_x_no_comp = self.x_no_comp#-self.x_average
			self.initial_y_no_comp = self.y_no_comp#-self.y_average
			self.initial_z_no_comp = self.z_no_comp#-self.z_average
			self.initial_x_comp    = self.x_compensated#-self.x_average
			self.initial_y_comp    = self.y_compensated#-self.y_average
			self.initial_z_comp    = self.z_compensated#-self.z_average


		self.counter += 1

		if self.thruster == 1:
			self.thrust1_pub.publish(output)
			self.thruster1_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster7_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw,self.roll_diff,self.pitch_diff,self.yaw_diff])
		elif self.thruster == 2:
			self.thrust2_pub.publish(output)
			self.thruster2_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp])#, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster8_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw])#,self.roll_diff,self.pitch_diff,self.yaw_diff])
		elif self.thruster == 3:
			self.thrust3_pub.publish(output)
			self.thruster3_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp])#, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster9_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw])#,self.roll_diff,self.pitch_diff,self.yaw_diff])
		elif self.thruster == 4:
			self.thrust4_pub.publish(output)
			self.thruster4_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp])# self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster10_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw])#,self.roll_diff,self.pitch_diff,self.yaw_diff])
		elif self.thruster == 5:
			self.thrust5_pub.publish(output)
			self.thruster5_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp])#, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster11_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw])#,self.roll_diff,self.pitch_diff,self.yaw_diff])
		elif self.thruster == 6:
			self.thrust6_pub.publish(output)
			self.thruster6_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster12_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw,self.roll_diff,self.pitch_diff,self.yaw_diff])
		else:
			self.thrust1_pub.publish(0.0)
			self.thrust2_pub.publish(0.0)
			self.thrust3_pub.publish(0.0)
			self.thrust4_pub.publish(0.0)
			self.thrust5_pub.publish(0.0)
			self.thrust6_pub.publish(0.0)						

		if self.counter == self.resolution + 1:
			self.counter = 0
			self.thruster += 1

			self.thrust1_pub.publish(0.0)
			self.thrust2_pub.publish(0.0)
			self.thrust3_pub.publish(0.0)
			self.thrust4_pub.publish(0.0)
			self.thrust5_pub.publish(0.0)
			self.thrust6_pub.publish(0.0)

			time_diff = 0
			start_time = time.time()*1000
			while self.stability == False:
				time_diff = time.time()*1000 - start_time
				if time_diff > 10000:
					self.initial_roll = self.new_roll
					self.initial_pitch = self.new_pitch
					self.initial_yaw = self.new_yaw
					break
				#print time_diff
				self.stable_rate.sleep()
			end_time = time.time()*1000
			time_diff = end_time - start_time

			rospy.loginfo(time_diff)

	def reverse(self):
		output = (float(self.counter)/self.resolution) * self.reverse_thrust_force

		if output == 0:
			self.initial_x_no_comp = self.x_no_comp#-self.x_average
			self.initial_y_no_comp = self.y_no_comp#-self.y_average
			self.initial_z_no_comp = self.z_no_comp#-self.z_average
			self.initial_x_comp    = self.x_compensated#-self.x_average
			self.initial_y_comp    = self.y_compensated#-self.y_average
			self.initial_z_comp    = self.z_compensated#-self.z_average

		self.counter += 1

		if self.thruster == 1:
			self.thrust1_pub.publish(output)
			self.thruster1_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster7_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw,self.roll_diff,self.pitch_diff,self.yaw_diff])
		elif self.thruster == 2:
			self.thrust2_pub.publish(output)
			self.thruster2_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp])#, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster8_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw])#,self.roll_diff,self.pitch_diff,self.yaw_diff])
		elif self.thruster == 3:
			self.thrust3_pub.publish(output)
			self.thruster3_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp])#, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster9_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw])#,self.roll_diff,self.pitch_diff,self.yaw_diff])
		elif self.thruster == 4:
			self.thrust4_pub.publish(output)
			self.thruster4_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp])#, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster10_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw])#,self.roll_diff,self.pitch_diff,self.yaw_diff])
		elif self.thruster == 5:
			self.thrust5_pub.publish(output)
			self.thruster5_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp])#, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster11_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw])#,self.roll_diff,self.pitch_diff,self.yaw_diff])
		elif self.thruster == 6:
			self.thrust6_pub.publish(output)
			self.thruster6_file.writerow([output,self.x_no_comp-self.initial_x_no_comp, self.y_no_comp-self.initial_y_no_comp, self.z_no_comp-self.initial_z_no_comp, self.x_compensated-self.initial_x_comp,self.y_compensated-self.initial_y_comp,self.z_compensated-self.initial_z_comp])
			self.thruster12_file.writerow([output,self.roll_diff_raw,self.pitch_diff_raw,self.yaw_diff_raw,self.roll_diff,self.pitch_diff,self.yaw_diff])
		else:
			self.thrust1_pub.publish(0.0)
			self.thrust2_pub.publish(0.0)
			self.thrust3_pub.publish(0.0)
			self.thrust4_pub.publish(0.0)
			self.thrust5_pub.publish(0.0)
			self.thrust6_pub.publish(0.0)						

		if self.counter == self.resolution + 1:
			self.counter = 0
			self.thruster += 1

			self.thrust1_pub.publish(0.0)
			self.thrust2_pub.publish(0.0)
			self.thrust3_pub.publish(0.0)
			self.thrust4_pub.publish(0.0)
			self.thrust5_pub.publish(0.0)
			self.thrust6_pub.publish(0.0)

			time_diff = 0
			start_time = time.time()*1000
			while self.stability == False:
				time_diff = time.time()*1000 - start_time
				if time_diff > 10000:
					self.initial_roll = self.new_roll
					self.initial_pitch = self.new_pitch
					self.initial_yaw = self.new_yaw
					break
				self.stable_rate.sleep()
			end_time = time.time()*1000
			time_diff = end_time - start_time

			rospy.loginfo(time_diff)		

	def stop_thrusters():
		thrust1_pub = rospy.Publisher('/thruster1_force', Float32, queue_size=1)
		thrust2_pub = rospy.Publisher('/thruster2_force', Float32, queue_size=1)
		thrust3_pub = rospy.Publisher('/thruster3_force', Float32, queue_size=1)
		thrust4_pub = rospy.Publisher('/thruster4_force', Float32, queue_size=1)
		thrust5_pub = rospy.Publisher('/thruster5_force', Float32, queue_size=1)
		thrust6_pub = rospy.Publisher('/thruster6_force', Float32, queue_size=1)

		thrust1_pub.publish(0.0)
		thrust2_pub.publish(0.0)
		thrust3_pub.publish(0.0)
		thrust4_pub.publish(0.0)
		thrust5_pub.publish(0.0)
		thrust6_pub.publish(0.0)

	def save_mag_values(self,data):
		self.x_compensated = data.magnetic_field.x
		self.y_compensated = data.magnetic_field.y
		self.z_compensated = data.magnetic_field.z		

		for i in range(self.window_size-1, -1, -1):
			self.sliderx[i] = self.sliderx[i-1]
			self.slidery[i] = self.slidery[i-1]
			self.sliderz[i] = self.sliderz[i-1]
		self.sliderx[0] = self.x_compensated
		self.slidery[0] = self.y_compensated
		self.sliderz[0] = self.z_compensated

		self.mag_avg_x = sum(self.sliderx)/self.window_size
		self.mag_avg_y = sum(self.slidery)/self.window_size
		self.mag_avg_z = sum(self.sliderz)/self.window_size

	def save_raw_mag_values(self,data):
		self.x_no_comp = data.mag_pre_comp_x
		self.y_no_comp = data.mag_pre_comp_y
		self.z_no_comp = data.mag_pre_comp_z		

		for i in range(self.window_size-1, -1, -1):
			self.no_comp_sliderx[i] = self.no_comp_sliderx[i-1]
			self.no_comp_slidery[i] = self.no_comp_slidery[i-1]
			self.no_comp_sliderz[i] = self.no_comp_sliderz[i-1]
		self.no_comp_sliderx[0] = self.x_no_comp
		self.no_comp_slidery[0] = self.y_no_comp
		self.no_comp_sliderz[0] = self.z_no_comp

		self.no_comp_mag_avg_x = sum(self.no_comp_sliderx)/self.window_size
		self.no_comp_mag_avg_y = sum(self.no_comp_slidery)/self.window_size
		self.no_comp_mag_avg_z = sum(self.no_comp_sliderz)/self.window_size

		if self.init_rpy2 == 0:
			self.initial_roll_raw = data.comp_roll
			self.initial_pitch_raw = data.comp_pitch
			self.initial_yaw_raw = data.comp_yaw
			self.init_rpy2 = 1

		self.new_roll_raw = data.comp_roll
		self.new_pitch_raw = data.comp_pitch
		self.new_yaw_raw = data.comp_yaw

		self.old_roll_raw = self.new_roll_raw
		self.old_pitch_raw = self.new_pitch_raw
		self.old_yaw_raw = self.new_yaw_raw

		self.roll_diff_raw = self.initial_roll_raw - data.comp_roll
		self.pitch_diff_raw = self.initial_pitch_raw - data.comp_pitch
		self.yaw_diff_raw = self.initial_yaw_raw - data.comp_yaw

	def save_rpy_values(self, data):

		if self.init_rpy == 0:
			self.initial_roll = data.roll
			self.initial_pitch = data.pitch
			self.initial_yaw = data.yaw
			#print self.initial_roll
			self.init_rpy = 1

		self.new_roll = data.roll
		self.new_pitch = data.pitch
		self.new_yaw = data.yaw

		if abs(self.initial_roll - self.new_roll) < self.sensitivity and abs(self.initial_pitch - self.new_pitch) < self.sensitivity and abs(self.initial_yaw - self.new_yaw) < self.sensitivity:
			self.stability = True
		else:
			self.stability = False

		self.old_roll = self.new_roll
		self.old_pitch = self.new_pitch
		self.old_yaw = self.new_yaw

		self.roll_diff = self.initial_roll - data.roll
		self.pitch_diff = self.initial_pitch - data.pitch
		self.yaw_diff = self.initial_yaw - data.yaw


	def create_files(self):
		date_time = strftime("%d_%m_%y_%H_%M_%S", localtime())
		file_name1 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster1_%s.csv" % date_time
		file_name2 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster2_%s.csv" % date_time
		file_name3 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster3_%s.csv" % date_time
		file_name4 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster4_%s.csv" % date_time
		file_name5 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster5_%s.csv" % date_time
		file_name6 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster6_%s.csv" % date_time

		file_name7 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster1_RPY_%s.csv" % date_time
		file_name8 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster2_RPY_%s.csv" % date_time
		file_name9 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster3_RPY_%s.csv" % date_time
		file_name10 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster4_RPY_%s.csv" % date_time
		file_name11 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster5_RPY_%s.csv" % date_time
		file_name12 = "/home/andy/catkin_ws/src/anglerfish/t100_thruster/data/thruster6_RPY_%s.csv" % date_time
		
		self.thruster1_file = csv.writer(open(file_name1,'w'))
		self.thruster1_file.writerow(["duty cycle","x_mag_raw","y_mag_raw","z_mag_raw", "x_mag_corr","y_mag_corr","z_mag_corr"])
		self.thruster2_file = csv.writer(open(file_name2,'w'))
		self.thruster2_file.writerow(["duty cycle","x_mag_raw","y_mag_raw","z_mag_raw"])#, "x_mag_corr","y_mag_corr","z_mag_corr"])		
		self.thruster3_file = csv.writer(open(file_name3,'w'))
		self.thruster3_file.writerow(["duty cycle","x_mag_raw","y_mag_raw","z_mag_raw"])#, "x_mag_corr","y_mag_corr","z_mag_corr"])
		self.thruster4_file = csv.writer(open(file_name4,'w'))
		self.thruster4_file.writerow(["duty cycle","x_mag_raw","y_mag_raw","z_mag_raw"])#, "x_mag_corr","y_mag_corr","z_mag_corr"])
		self.thruster5_file = csv.writer(open(file_name5,'w'))
		self.thruster5_file.writerow(["duty cycle","x_mag_raw","y_mag_raw","z_mag_raw"])#, "x_mag_corr","y_mag_corr","z_mag_corr"])
		self.thruster6_file = csv.writer(open(file_name6,'w'))
		self.thruster6_file.writerow(["duty cycle","x_mag_raw","y_mag_raw","z_mag_raw", "x_mag_corr","y_mag_corr","z_mag_corr"])

		self.thruster7_file = csv.writer(open(file_name7,'w'))
		self.thruster7_file.writerow(["duty cycle","roll_raw","pitch_raw","yaw_raw", "roll_corr","pitch_corr","yaw_corr"])
		self.thruster8_file = csv.writer(open(file_name8,'w'))
		self.thruster8_file.writerow(["duty cycle","roll_raw","pitch_raw","yaw_raw"])#, "roll_corr","pitch_corr","yaw_corr"])
		self.thruster9_file = csv.writer(open(file_name9,'w'))
		self.thruster9_file.writerow(["duty cycle","roll_raw","pitch_raw","yaw_raw"])#, "roll_corr","pitch_corr","yaw_corr"])
		self.thruster10_file = csv.writer(open(file_name10,'w'))
		self.thruster10_file.writerow(["duty cycle","roll_raw","pitch_raw","yaw_raw"])#, "roll_corr","pitch_corr","yaw_corr"])
		self.thruster11_file = csv.writer(open(file_name11,'w'))
		self.thruster11_file.writerow(["duty cycle","roll_raw","pitch_raw","yaw_raw"])#, "roll_corr","pitch_corr","yaw_corr"])
		self.thruster12_file = csv.writer(open(file_name12,'w'))
		self.thruster12_file.writerow(["duty cycle","roll_raw","pitch_raw","yaw_raw", "roll_corr","pitch_corr","yaw_corr"])

	def __init__(self):
		self.rate = rospy.Rate(25)

		self.thrust1_pub = rospy.Publisher('/thruster1_force', Float32, queue_size=1)
		self.thrust2_pub = rospy.Publisher('/thruster2_force', Float32, queue_size=1)
		self.thrust3_pub = rospy.Publisher('/thruster3_force', Float32, queue_size=1)
		self.thrust4_pub = rospy.Publisher('/thruster4_force', Float32, queue_size=1)
		self.thrust5_pub = rospy.Publisher('/thruster5_force', Float32, queue_size=1)
		self.thrust6_pub = rospy.Publisher('/thruster6_force', Float32, queue_size=1)

		rospy.Subscriber('/imu/mag', MagneticField, self.save_mag_values)
		rospy.Subscriber('/mag_raw_rpy', mag_raw, self.save_rpy_values)
		rospy.Subscriber("/comp_mag_values", mag_values, self.save_raw_mag_values)

		self.window_size = 200
		self.sliderx = [0] * self.window_size
		self.slidery = [0] * self.window_size
		self.sliderz = [0] * self.window_size

		self.no_comp_sliderx = [0] * self.window_size
		self.no_comp_slidery = [0] * self.window_size
		self.no_comp_sliderz = [0] * self.window_size

		self.initial_x_no_comp = 0
		self.initial_y_no_comp = 0
		self.initial_z_no_comp = 0
		self.initial_x_comp    = 0
		self.initial_y_comp    = 0
		self.initial_z_comp    = 0

		self.counter = 0
		self.thruster = 1
		self.resolution = 200.0
		self.forward_thrust_force = 1 #2.36 kg forward
		self.reverse_thrust_force = -1 #1.82 kg reverse
		self.direction = 'forward'
		self.init_rpy = 1
		self.init_rpy2 = 1
		self.roll_diff = 0.0
		self.pitch_diff = 0.0
		self.yaw_diff = 0.0

		self.new_roll = 0.0
		self.new_pitch = 0.0
		self.new_yaw = 0.0
		self.old_roll = 0.0
		self.old_pitch = 0.0
		self.old_yaw = 0.0
		self.initial_roll = 0.0
		self.initial_pitch = 0.0
		self.initial_yaw = 0.0
		self.initial_roll_raw = 0.0
		self.initial_pitch_raw = 0.0
		self.initial_yaw_raw = 0.0
		self.stable = False
		self.stable_rate = rospy.Rate(20)
		self.sensitivity = 0.05



		self.mag_rate = rospy.Rate(25) #15

		rospy.loginfo("******************** Thruster vs Mag calibration ********************")
		rospy.loginfo("Starting mag averaging, hold sub very still...")
		for i in range (0,self.window_size +1):
			self.mag_rate.sleep()

		self.x_average = self.mag_avg_x
		self.y_average = self.mag_avg_y
		self.z_average = self.mag_avg_z

		rospy.loginfo("Mag averaging complete: %f" % self.x_average)

		while self.new_roll == 0.0:
			self.stable_rate.sleep()
		self.init_rpy = 0
		self.init_rpy2 = 0

		self.create_files()
		self.arm_thrusters()		



		while not rospy.is_shutdown():
			if self.counter == 0:
				rospy.loginfo("Starting thruster: %d, direction: %s" % (self.thruster, self.direction))

			if self.direction == 'forward':
				self.forward()
			elif self.direction == 'reverse':
				self.reverse()

			if self.thruster == 7 and self.direction == 'forward':
				self.thruster = 1
				self.direction = 'reverse'
				self.init_rpy = 0  ######
				self.init_rpy2 = 0  ######
			elif self.thruster == 7 and self.direction == 'reverse':
				self.direction = 'stop'
				rospy.loginfo("Thruster testing complete")
				rospy.signal_shutdown('Complete')


			self.rate.sleep()
			#rospy.spin()
	
	rospy.on_shutdown(stop_thrusters)

def main(args):
	rospy.init_node('thruster_test', anonymous=False)

	start_test()

        try:
		rospy.spin()
        except rospy.ROSInterruptException:
		print "Shutting down"
                pass
	


if __name__ == '__main__':
	main(sys.argv)
