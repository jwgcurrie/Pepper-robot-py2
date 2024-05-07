#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

#TODO - Head orientation could be controlled through mouse
#TODO - Camera/IR Sensor monitor for operator

import qi
import argparse
import sys
import math
import almath
import time
import os
import pygame


pygame.init()
display = pygame.display.set_mode((300, 300))

v_x = 0.2
v_theta = 0.8


def main(session):
    awareness_service = session.service("ALBasicAwareness")
    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")
    LED_service = session.service("ALLeds")

    eye_LEDs = ["FaceLedRight0", "FaceLedRight1", "FaceLedRight2", "FaceLedRight3", "FaceLedRight4", "FaceLedRight5", "FaceLedRight6", "FaceLedRight7",
                "FaceLedLeft0", "FaceLedLeft1", "FaceLedLeft2", "FaceLedLeft3", "FaceLedLeft4", "FaceLedLeft5", "FaceLedLeft6", "FaceLedLeft7"]
    LED_service.createGroup("Eyes", eye_LEDs)
    LED_service.fadeRGB("Eyes", 'blue', 1)

    # Wake up robot
    motion_service.wakeUp()

    # Send robot to Stand Init
    posture_service.goToPosture("StandInit", 0.5)
    awareness_service.setEnabled(True)
    awareness_service.setTrackingMode("Head")  

    while 1:
        InputWasd(motion_service, posture_service)


def MotionMapping_x(motion_service, command_x):
    command_x = command_x * v_x
    motion_service.move(command_x, 0, 0)

def MotionMapping_theta(motion_service, command_theta):
    command_theta = command_theta * v_theta
    motion_service.move(0, 0, command_theta)

def InputWasd(motion_service, posture_service):
ww
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_w:
                command_x = 1
                MotionMapping_x(motion_service, command_x)
            if event.key == pygame.K_s:
                command_x = -1
                MotionMapping_x(motion_service, command_x)
            if event.key == pygame.K_a:
                command_theta = 1
                MotionMapping_theta(motion_service, command_theta)            
            if event.key == pygame.K_d:
                command_theta = -1
                MotionMapping_theta(motion_service, command_theta)  
            if event.key == pygame.K_LSHIFT:
                command_x = 0
                command_theta = 0
                MotionMapping_x(motion_service, command_x)
                MotionMapping_theta(motion_service, command_theta)
            if event.key == pygame.K_0:
                #posture_service.goToPosture("Crouch", 0.5)
                motion_service.rest()
            if event.key == pygame.K_1:
                #posture_service.goToPosture("Stand", 0.5)
                motion_service.wakeUp()

1




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.0.4",
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.0.4'")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
            "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)