#! /usr/bin/env python
# -*- encoding: UTF-8 -*-


import qi
import argparse
import sys
import math
import almath
import time
import os
import datetime
#import pandas as pd
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt



def main(session):
    awareness_service = session.service("ALBasicAwareness")
    memory_service = session.service("ALMemory")
    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")
    gaze_service = session.service("ALGazeAnalysis")
    face_service = session.service("ALFaceDetection")
    people_service = session.service("ALPeoplePerception")
    user_service = session.service("ALUserSession")
    user_info_service = session.service("ALUserInfo")
    tracker_service = session.service("ALTracker")
    LED_service = session.service("ALLeds")

    # Initialise data output 
    [subject_ID, file_path]  = DataOutSetup()
    

    # Wake up robot
    motion_service.wakeUp()

    # Send robot to Stand Init
    posture_service.goToPosture("StandInit", 0.5)
    awareness_service.setEnabled(True)
    awareness_service.setTrackingMode("MoveContextually")  
    gaze_service.subscribe("gaze_subscriber")
    
    #plt.axis([0, 10, 0, 1])

    start = time.time()
    start0 = start
    while(True):     
        end = time.time()

        
        if end-start > 0.1:

            now = datetime.datetime.now()
            personID = VisiblePeopleRecognised(memory_service)
            GazeScore = GazeScoreOut(memory_service, personID)
            #print("Gaze: " + str(GazeScore * 100) + "%")
            writeData = [str(subject_ID), str(now), str(GazeScore)]

            plt.scatter(time.time(), GazeScore)
            plt.pause(0.01)

            with open(file_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(writeData)

            start = time.time()





def DataOutSetup():
    # Input ID:
    subject_ID = raw_input("Enter participant ID: ")
    # Get current working dir 
    current_dir = os.path.dirname(__file__)
    # Create path including working dir 
    file_path = os.path.join(current_dir, "gazeOut.csv")     
    return subject_ID, file_path

def GazeScoreOut(memory_service, personID):
    address = "PeoplePerception/Person/" + str(personID) + "/LookingAtRobotScore"
    try:
        LookingAtRobotScore = memory_service.getData(address)
        #print(LookingAtRobotScore)
        return LookingAtRobotScore
    except: 
        print("Error - GazeScoreOut: no data found")


def VisiblePeopleRecognised(memory_service):
    people_detected = memory_service.getData("PeoplePerception/PeopleDetected")
    while people_detected :
        vis_people_list = memory_service.getData("PeoplePerception/VisiblePeopleList")
            
        if len(vis_people_list) > 0:
            for personID in vis_people_list:                  
                address = "PeoplePerception/Person/" + str(personID) + "/IsFaceDetected"
                if memory_service.getData(address):
                    return personID
      
def Follow(tracker_service, LED_service, target):
    LED_service.fadeRGB('FaceLedsBottom', 'green', 1)
    tracker_service.registerTarget('People', target)
    tracker_service.setMode("Navigate")
    tracker_service.track('People')
    LED_service.fadeRGB('FaceLedsBottom', 'white', 1)



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