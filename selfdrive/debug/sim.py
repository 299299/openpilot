#!/usr/bin/env python3
import os
import time
import math
import atexit
import numpy as np
import threading
import random
import cereal.messaging as messaging
from cereal import log
import argparse
from common.params import Params
from common.realtime import Ratekeeper
from selfdrive.car.honda.values import CruiseButtons
import subprocess
import sys
import signal
import threading
from queue import Queue
from selfdrive.debug.can import can_function, sendcan_function
from selfdrive.debug.keyboard_ctrl import keyboard_poll_thread, keyboard_shutdown

params = Params()

def send_peripherl(pm):
  dat = messaging.new_message('peripheralState')
  dat.valid = True
  # fake peripheral state data
  dat.peripheralState = {
    'pandaType': "uno",
    'voltage': 12000,
    'current': 5678,
    'fanSpeedRpm': 1000
  }
  pm.send('peripheralState', dat)

def send_ignition(ignition, pm):
  dat = messaging.new_message('pandaStates', 1)
  dat.valid = True
  dat.pandaStates[0] = {
    'ignitionLine': ignition,
    'pandaType': "uno",
    'controlsAllowed': True,
    'safetyModel': 'hondaNidec',
    'safetyRxChecksInvalid': False,
    'alternativeExperience':1
  }
  pm.send('pandaStates', dat)

def send_dms(pm):
  pm = messaging.PubMaster(['driverStateV2', 'driverMonitoringState'])
  # dmonitoringmodeld output
  dat = messaging.new_message('driverStateV2')
  dat.driverStateV2.leftDriverData.faceOrientation = [0., 0., 0.]
  dat.driverStateV2.leftDriverData.faceProb = 1.0
  dat.driverStateV2.rightDriverData.faceOrientation = [0., 0., 0.]
  dat.driverStateV2.rightDriverData.faceProb = 1.0
  pm.send('driverStateV2', dat)

  # dmonitoringd output
  dat = messaging.new_message('driverMonitoringState')
  dat.driverMonitoringState = {
    "faceDetected": True,
    "isDistracted": False,
    "awarenessStatus": 1.,
  }
  pm.send('driverMonitoringState', dat)

def shutdown():
  global params
  global pm

  print('shutdown !')

  keyboard_shutdown()

  for seq in range(10):
    send_ignition(False, pm)
    time.sleep(0.1)

  print ("exiting")
  sys.exit(0)

def main():

  global params
  global pm

  # make volume 0
  #os.system('service call audio 3 i32 3 i32 0 i32 1')

  #params.delete("Offroad_ConnectivityNeeded")

  q = Queue()

  t = threading.Thread(target=keyboard_poll_thread, args=[q])
  t.start()

  pm = messaging.PubMaster(['can', 'pandaStates', 'peripheralState'])
  sm = messaging.SubMaster(['carControl'])

  # can loop
  rk = Ratekeeper(100, print_delay_threshold=None)
  steer_angle = 0.0
  speed = 30.0 / 3.6
  cruise_button = 0

  btn_list = []
  btn_hold_times = 2

  frames = 0

  left_blinker = 0
  right_blinker = 0

  while 1:
    # check keyboard input
    if not q.empty():
      message = q.get()
      #print (message)

      if (message == 'quit'):
        shutdown()
        return

      if message == 'left_light':
        if left_blinker == 1:
          left_blinker = 0
        else:
          left_blinker = 1

        print ('left_blinker=', left_blinker)
        continue

      if message == 'right_light':
        if right_blinker == 1:
          right_blinker = 0
        else:
          right_blinker = 1

        print ('right_blinker=', right_blinker)
        continue

      if message == 'speed_up':
        speed += 5.0 / 3.6

      if message == 'speed_down':
        speed -= 5.0 / 3.6

      m = message.split('_')
      if m[0] == "cruise":
        if m[1] == "down":
          cruise_button = CruiseButtons.DECEL_SET
          if len(btn_list) == 0:
            for x in range(btn_hold_times):
              btn_list.append(cruise_button)
        if m[1] == "up":
          cruise_button = CruiseButtons.RES_ACCEL
          if len(btn_list) == 0:
            for x in range(btn_hold_times):
              btn_list.append(cruise_button)
        if m[1] == "cancel":
          cruise_button = CruiseButtons.CANCEL
          if len(btn_list) == 0:
            for x in range(btn_hold_times):
              btn_list.append(cruise_button)

    btn = 0
    if len(btn_list) > 0:
      btn = btn_list[0]
      btn_list.pop(0)

    # print ('cruise_button=', cruise_button)
    can_function(pm, speed, steer_angle, rk.frame, cruise_button=btn, is_engaged=1)
    if rk.frame%5 == 0:
      #throttle, brake, steer = sendcan_function(sendcan)
      #steer_angle += steer/10000.0 # torque
      #print(speed * 3.6, steer, throttle, brake)
      pass

    if frames % 20 == 0:
      send_ignition(True, pm)
      send_peripherl(pm)
      #send_dms(pm)

    frames += 1

    rk.keep_time()

  shutdown()

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    shutdown()

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)

  print (sys.argv)
  print ("input 1 to curse resume/+")
  print ("input 2 to curse set/-")
  print ("input 3 to curse cancel")
  print ("input 4 to left light")
  print ("input 5 to right light")
  print ("input 6 to speed up")
  print ("input 7 to speed down")
  print ("input q to quit")

  main()

