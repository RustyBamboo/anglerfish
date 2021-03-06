#!/usr/bin/env python
import rospy
import rosparam
import random
import numpy as np
import matplotlib.pyplot as plt
import time

from std_msgs.msg import Header
from pinger_tracker.msg import *
from multilateration import Multilaterator
import multilateration as mlat
from time_signal_1d import TimeSignal1D

import time
import sys
import os

class phaser(Multilaterator):

    def hydrophone_locations(self, data):
        self.hydro0 = [data.hydro0_xyz[0],data.hydro0_xyz[1],data.hydro0_xyz[2]]
        self.hydro1 = [data.hydro1_xyz[0],data.hydro1_xyz[1],data.hydro1_xyz[2]]
        self.hydro2 = [data.hydro2_xyz[0],data.hydro2_xyz[1],data.hydro2_xyz[2]]
        self.hydro3 = [data.hydro3_xyz[0],data.hydro3_xyz[1],data.hydro3_xyz[2]]

    def pinger_position(self, tstamps):
        hydrophone_locations = np.array([self.hydro0, self.hydro1, self.hydro2, self.hydro3])

        c = 1.484  # millimeters/microsecond
        #hydrophone_array = ReceiverArraySim(hydrophone_locations, c)
        sonar = Multilaterator(hydrophone_locations, c, 'bancroft')

        res_msg = sonar.get_pulse_location(np.array(tstamps))
        #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        print res_msg
        
        #res = np.array([res_msg[0], res_msg[1], res_msg[2]])

    def a_add_zeros(self, a_sig):
        channel_length = len(a_sig)

        if channel_length % 2 != 0:
            zeros = [0]*(channel_length+1)
        else:
            zeros = [0]*(channel_length)      

        signed = [-(2**self.bit)/2]*channel_length

        a_sig = list(a_sig)
        a_sig = [x + y for x, y in zip(a_sig, signed)]     

        signal = zeros + a_sig

        return signal        


    def ref_add_zeros(self, ref_sig):
        channel_length = len(ref_sig)

        if channel_length % 2 != 0:
            zeros = [0]*(channel_length+1)
        else:
            zeros = [0]*(channel_length)      

        signed = [-(2**self.bit)/2]*channel_length

        ref_sig = list(ref_sig)
        ref_sig = [x + y for x, y in zip(ref_sig, signed)]   
        
        reference = zeros[channel_length/2:] + ref_sig + zeros[:channel_length/2+1]           

        return reference


    def determine_phase(self, ref_sig, a_sig):
        channel_length = len(ref_sig)

        signal = self.a_add_zeros(a_sig)
       
        reference = self.ref_add_zeros(ref_sig)

        length = len(reference)
        
        sum_val = 0
        sum_val_max = 0
        phase_holder = 0
        max_list = []

        cross_corr = np.correlate(reference, signal, mode='full')
        max_idx = cross_corr.argmax()
        
        phase_holder = 2*channel_length-1 - max_idx    

        #print float(channel_length/2-phase_holder)
        return (channel_length/2-phase_holder)*(1.0/self.sample_rate)
        #return (channel_length/2-max_idx)*(1.0/self.sample_rate)

    def actual(self, data):
        self.actual_stamps = data.actual_time_stamps

    def parse_ping(self, data):        
        self.bit = data.adc_bit
        self.sample_rate = data.sample_rate
        self.actual_position = data.actual_position
        Ts = 1.0/self.sample_rate
        signal_periods = 1.0/25000.0
        channel_length = len(data.data)/data.channels


        self.signal = []
        self.timestamps = []

        for i in range(data.channels):
            self.signal.append([])
            self.signal[i] = data.data[i::4]
            left_periods = int((channel_length/2)-signal_periods/Ts)
            right_periods = int((channel_length/2)+signal_periods/Ts)
            #print self.signal
            self.signal[left_periods:right_periods]

        #self.ref_signal = [None]*(channel_length)
        #self.ref_signal = data.data[::4]
        #self.a_signal = [None]*(channel_length)
        #self.a_signal = data.data[1::4]
        
        #print "***"
        self.start = time.clock()


        '''
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% David's Code %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        signal_zero = self.signal

        signal_zero[0] = self.ref_add_zeros(self.signal[0])
        signal_zero[1] = self.a_add_zeros(self.signal[1])
        signal_zero[2] = self.a_add_zeros(self.signal[2])
        signal_zero[3] = self.a_add_zeros(self.signal[3])
        print signal_zero

        ref_signal = mlat.TimeSignal1D(samples=np.array(signal_zero[0]), sampling_freq=self.sample_rate)
        non_ref_signals = [mlat.TimeSignal1D(samples=np.array(signal), sampling_freq=self.sample_rate) for signal in signal_zero[1:]]
        #non_ref_signals = mlat.TimeSignal1D(samples=np.array(self.signal[1]), sampling_freq=self.sample_rate)
        #print non_ref_signals[0].samples
        dtoa, cross_corrs = mlat.get_dtoas(ref_signal, non_ref_signals)

        print""
        #print dtoa
        print ""
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'''
        self.timestamps = [0.0]
        for i in range(3):
            self.timestamps.append(self.determine_phase(self.signal[0], self.signal[i+1]))

        self.end = time.clock()
        os.system('clear')

        #sys.stderr.write("\x1b[2J\x1b[H")
        #print type(self.actual_stamps)
        #print type(timestamps)
        #difference = list(self.actual_stamps) - timestamps
        microseconds = [1e6,1e6,1e6,1e6]
        print "*********************************"
        print ("{}time to perform timestamps (Sec): {}%0.3f{}\n".format(self.W,self.O,self.W) % (self.end-self.start))
        #[0.0, 3.3333333333333333e-06, 0.0, 1.9999999999999998e-05]
        calculated = [x * y for x, y in zip(self.timestamps,microseconds)]

        self.calc_stamps_pub.publish(Calculated_time_stamps(
            header=Header(stamp=rospy.Time.now(),
                          frame_id='phase_shift'),
            calculated_time_stamps=calculated))

        print "{}calculated timestamps (uSec):".format(self.W)

        print "\t" + str(calculated)
        print "actual timestamps (uSec):"
        print "\t" + str(self.actual_stamps) #str([x * y for x, y in zip(self.actual_stamps,microseconds)])
        print "difference (uSec):"
        self.timestamps = [x * y for x, y in zip(self.timestamps,microseconds)]
        difference = [x - y for x, y in zip(list(self.actual_stamps), self.timestamps)]
        #difference = [x * y for x, y in zip(difference,microseconds)]
        print "\t" + str(difference)
        errors = sum(map(abs, difference))
        print "Absolute sum of errors (uSec): {}%0.3f{}".format('\033[43m',self.W) % errors
       #mult = Multilaterator()
        #******************** figure out how to transfer variables from Multilateration ********************
        #self.pinger_position(calculated)
        #*****************************************************************************************************
        #print 

        #print "Actual position:\n\t" + "x: " + str(self.actual_position[0]) + " y: " + str(self.actual_position[1]) \
                #+ " z: " + str(self.actual_position[2]) + " (mm){}\n".format(self.W)        
        #print "*********************************"

    def __init__(self):

        self.start = time.clock()
        self.end = time.clock()
        self.timestamps = []
        self.actual_stamps = []
        self.actual_position = [0,0,0]

        self.hydro0 = [0,     0,     0]
        self.hydro1 = [-25.4, 0,     0]
        self.hydro2 = [25.4,  0,     0]
        self.hydro3 = [0,     -25.4, 0]

        rospy.Subscriber('hydrophones/hydrophone_locations', Hydrophone_locations, self.hydrophone_locations)
        rospy.Subscriber('/hydrophones/actual_time_stamps', Actual_time_stamps, self.actual)
        self.calc_stamps_pub = rospy.Publisher('/hydrophones/calculated_time_stamps', Calculated_time_stamps, queue_size = 1)
        #self.ls_pub = rospy.Publisher('hydrophones/Ls_pos', LS_pos, queue_size = 1)

        self.W  = '\033[0m'  # white (normal)
        self.R  = '\033[31m' # red
        self.G  = '\033[32m' # green
        self.O  = '\033[43m' # orange
        self.B  = '\033[34m' # blue
        self.P  = '\033[35m' # purple        
        
        rospy.init_node('phase_shift')

        rospy.Subscriber('/hydrophones/ping', Ping, self.parse_ping)

        rate = rospy.Rate(1)  #rate of signals, 5 Hz for Anglerfish

        while not rospy.is_shutdown():

            rate.sleep()


def main():
    rospy.init_node('phase_shift', anonymous=False)

    phaser()

    try:
        rospy.spin()
    except rospy.ROSInterruptException:
        print "Shutting down"
        pass
    


if __name__ == '__main__':
    main()