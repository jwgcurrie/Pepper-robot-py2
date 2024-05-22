#! /usr/bin/env python
# -*- encoding: UTF-8 -*-


import qi
import argparse
import sys
import math
import almath
import time
import os
import pygame

# Modes 'keyboard' 'dualshock' 

Mode = 'dualshock'
Effectors = ['Move', 'Head']


pygame.init()
pygame.joystick.init()
controller = pygame.joystick.Joystick(0)
controller.init()

Controller_square_button_state = 0
v_x = 0.15
v_theta = 0.5
joint_speed_frac = 0.1


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
    motion_service.setTangentialSecurityDistance(0.05)
    motion_service.setOrthogonalSecurityDistance(0.2)

    # Send robot to Stand Init
    posture_service.goToPosture("StandInit", 0.5)
    awareness_service.setEnabled(True)
    awareness_service.setTrackingMode("Head")  

    

    while 1:
        if Mode == 'dualshock':
            joyaxis(motion_service, Effectors)
        if Mode == 'keyboard':
            InputWasd(motion_service, posture_service)



def MotionMapping(motion_service, effector, Controller_LX, Controller_LY, Controller_RX, Controller_RY):
    if effector == 'Move':
        command_x = -round(Controller_LY, 1) * v_x
        command_theta = -round(Controller_R, 1) * v_theta
        motion_service.move(command_x, 0, command_theta)
    elif effector == 'Head':
        command_yaw = -round(Controller_LX, 1) * 2 # Max value: 2.0857
        command_pitch = round(Controller_R, 1) * 0.4 # Max Value: 0.4451
        motion_service.setAngles(['HeadYaw', 'HeadPitch'], [command_yaw, command_pitch], joint_speed_frac) # TODO - bug yaw goes to extreme not obeying speed limits
    elif effector == 'Move_XY':
        command_x = -round(Controller_LY, 1) * v_x
        command_y = -round(Controller_LX, 1) * v_x
        command_theta = -round(Controller_RY, 1) * v_theta
        print(command_x, command_y, command_theta)
        motion_service.move(command_x, command_y, command_theta)



def joyaxis(motion_service, Effectors):
    for event in pygame.event.get():
        # Read button events
        global Controller_square_button_state
        Controller_square_button_state = Controller_square_button_state + controller.get_button(2)
        if Controller_square_button_state > 1:
            Controller_square_button_state = 0

        # Read joystick axis events
        Controller_Left_X = controller.get_axis(pygame.CONTROLLER_AXIS_LEFTX)
        Controller_Left_Y = controller.get_axis(pygame.CONTROLLER_AXIS_LEFTY)
        Controller_Right_X = controller.get_axis(pygame.CONTROLLER_AXIS_RIGHTX)
        Controller_Right_Y = controller.get_axis(pygame.CONTROLLER_AXIS_RIGHTY)

        effector = Effectors[Controller_square_button_state]

        MotionMapping(motion_service, effector, Controller_Left_X, Controller_Left_Y, Controller_Right_X, Controller_Right_X)





def InputWasd(motion_service, posture_service):

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