#!/usr/bin/python
# -*- coding: utf-8 -*-
# combines guidetest.py, listtest.py, videoplayback.py, and ________ anthony

# StormTestClient API

import stormtest.ClientAPI as StormTest
import time
import datetime
import slotClass  # holds definitons for model and version of STB
import sys
import os
import json
import errno
import SThelperNew
from RackLib import RackLib

#########################################################
###################  Constants  #########################
#########################################################

MAXDELAY = 10
BUTTON_PRESS_DELAY = 2
MAX_ATTEMPTS = 10
CHANNEL = 206
PLAYBACK_TOLERANCE = 98  # percent match between the 2 frames
MODEL = 0
VERSION = 1
TEST_NAME = 'Output.txt Test'
FORMAT = 'Format'
TESTREPORT = 'TestReport'

#########################################################
#################  IR COMMAND NAMES #####################
#########################################################
ACTIVE = 'Active'
ADVANCE = 'Advance'
ARROW_DOWN = 'Down'
ARROW_LEFT = 'Left'
ARROW_RIGHT = 'Right'
ARROW_UP = 'Up'
BLUE = 'Blue'
CHANNEL_DOWN = 'Channel-'
CHANNEL_UP = 'Channel+'
DASH = 'Dash'
ENTER = 'Enter'
EXIT = 'Exit'
FORMAT = 'Format'
FORWARD = 'FFwd'
GREEN = 'Green'
GUIDE = 'TV_Guide'
INFO = 'Info'
LIST = 'List'
MENU = 'Menu'
OK = 'Ok'
PAUSE = 'Pause'
PLAY = 'Play'
PLAY_PAUSE = 'PlayPause'
POWER = 'Power'
PREVIOUS = 'Prev'
RECORD = 'Record'
RED = 'Red'
REPLAY = 'Replay'
REWIND = 'Rew'
#SELECT = 'Select'
SELECT = 'Ok'
STOP = 'Stop'
VOLUMN_DOWN = 'Vol-'
VOLUMN_UP = 'Vol+'
YELLOW = 'Yellow'

#SLOT = '3'
#RACK = '8'
#TARGET_RESOLUTION = '1080i'
#testID = 0
#ssinfo = {}
#ssinfo[TESTREPORT] = []
#startTime = 0


refRegionResource = '/CompareScreenRectResource'
refImageResource = '/RefImageResource'
poweroffpicpath = "screenshots\powerOff2.stscreen"
espnpicpath = "screenshots\espnhd_2.stscreen"  # 2nd from top of guide (graphic is top line)
espnpicpath2 = "screenshots\espnhd2_2.stscreen"  # top of guide
main_menu_path = "screenshots\MainMenu_2.stscreen"
settings_and_help_path = "screenshots\SettingsAndHelp_2.stscreen"
resolution_path = 'screenshots\\resolution.stscreen'
poweroffpic = 'powerOff.stscreen'
screenshotpath = 'snapshot_screenshots'
pathtolog = 'D:\\STDaemon\\Logs\\public\\Joe\\snapshot_screenshots'
pathtolog4 = \
    'D:\\STDaemon\\Logs\\public\\Snapshot\\snapshot_screenshots'
pathtolog4_2 = '..\\snapshot_screenshots'
settings_info_path = "screenshots\SettingsInfoMUI.stscreen"
output_file_name = 'output'

#########################################################
#########################################################

# Return value flag
returnValue = 1

#########################################################
#############<><><> HELPER FUNCTIONS <><><><>############
#########################################################
#exit any menu and attempt to have only live tv with no OSD on screen
def exitmenus():
    StormTest.PressButton(EXIT)
    StormTest.WaitSec(3)
    StormTest.PressButton(SELECT) #in case there is an error on screen
    StormTest.WaitSec(3)
    StormTest.PressButton(EXIT)
    StormTest.WaitSec(3)
#wake up the box from standby
def wakebox():
    StormTest.PressButton(INFO)
    StormTest.WaitSec(3)
    StormTest.PressButton(INFO)
    StormTest.WaitSec(3)
    exitmenus()
    exitmenus()
    SThelperNew.takeScreenshot('Wake up Boxes', 'Are boxes awake? (Live TV Displays)')
#create a user specified streaming buffer, up to a maximum of 90 minutes
def createbuffer(minutes):
    maxbuffer = 90 #90 minutes
    try:
        if minutes > maxbuffer: minutes = maxbuffer #change to minutes
        seconds = minutes * 60 #convert minutes to seconds, formula is minutes x 60s/min
        exitmenus() #make sure nothing is on screen preventing the buffer from being created
        StormTest.WaitSec(seconds)
    except:
        SThelperNew.takeScreenshot('No Buffer', 'No buffer was created, troubleshoot code createbuffer')
        return
#Pause then play the feed. Two functions in one!
def pauseplay():
    exitmenus()
    StormTest.PressButton(PAUSE)
    StormTest.WaitSec(3)
    StormTest.PressButton(PLAY)
    StormTest.WaitSec(3)
    SThelperNew.takeScreenshot("Play Live", "Live TV should be playing")
#Pause any feed. Will remain paused.
def pausefeed():
    StormTest.PressButton(PAUSE)
    StormTest.WaitSec(3)
    SThelperNew.takeScreenshot('Feed Pause', 'Box is in a Paused state')
#Play any feed
def playfeed():
    StormTest.PressButton(PLAY)
    StormTest.WaitSec(3)
    SThelperNew.takeScreenshot('Play Feed', 'Box is in a playing state')
#rewind function, call and input a velocity ie rewind(2)
def rewind(rvelocity):
    rspeed = [1, 2, 3, 4]
    ivarr = 0 #iteration variable for loop

    #if the specified velocity is invalid, spill error and exit function
    if rvelocity not in rspeed:
        return SThelperNew.takeScreenshot('No Rewind', 'No rewind occured, ensure valid input is added (1-4).')
    try:
        #iterate through rspeed list
        for rnum in range(len(rspeed)):
            #check whether rvelocity matches rspeed at rnum index
            if rspeed[rnum] == rvelocity:
                #Send IR commands until reaching the specified rvelocity
                while ivarr < rvelocity:
                    StormTest.PressButton(REWIND)
                    StormTest.WaitSec(3)
                    ivarr += 1
                #print out test case with corresponding rvelocity
                SThelperNew.takeScreenshot('Rewind test at x' + str(rvelocity), 'Box is rewinding at x' + str(rvelocity) + ' speed.')
                #break loop after this to save computation time
                break
    except:
        SThelperNew.takeScreenshot('No Rewind', 'Valid Input given but no rewind occured, check body of rewind function')
        return

#forward function, call and input a velocity, ie foward(2)
def forward(fvelocity):
    fspeed = [1, 2, 3, 4]
    ivarf = 0 #loop iteration variable

    #if the specified fvelocity is not in fspeed, error out and exit function
    if fvelocity not in fspeed:
        return SThelperNew.takeScreenshot('No Forward', 'No forward occured, ensure valid input is added (1-4)')
    try:
        #iterate through fspeed list
        for fnum in range(len(fspeed)):
            #check whether fvelocity matches fspeed at fnum index
            if fspeed[fnum] == fvelocity:
                #send IR commands until reaching the specified fvelocity
                while ivarf < fvelocity:
                    StormTest.PressButton(FORWARD)
                    StormTest.WaitSec(3)
                    ivarf += 1
                #print out test case with corresponding fvelocity
                SThelperNew.takeScreenshot('Forward test at x' + str(fvelocity), 'Box is forwarding at x' + str(fvelocity) + ' speed.')
                #break out of loop to save computation time
                break
    except:
        SThelperNew.takeScreenshot('No Forward', 'Valid input given but no forward occured, check main body of forward function')
        return
#Advance forward x amount of times and print out corresponding advance speed. Range from 1-20. Note: create a long buffer for over 10.
def advance(avelocity):
    #dictionary for every state of the advance feature, where key is the input (how many times advanced is pressed), and value is the corresponding advance time.
    adict = { 1: '30s', 2: '1m', 3: '1m30s', 4: '2m', 5: '2m30s', 6: '3m', 7: '3m30s', 8: '4m', 9: '4m30s', 10: '5m',
            11: '5m30s', 12: '6m', 13: '6m30s', 14: '7m', 15: '7m30s', 16: '8m', 17: '8m30s', 18: '9m', 19: '9m30s', 20: '10m'}
    ivara = 0 #loop iteration variable
    #if the specified avelocity is not a valid key in adic, quit out of function
    if avelocity not in adict:
        return SThelperNew.takeScreenshot('No Advance', 'No advance occured, ensure valid input is added (1-20)')
    try:
        #iterate through adic dictionary. items() returns a tuple, hence the for loop has key, value pair
        for key, value in adict.items():
            #find the correct key corresponding with avelocity
            if key == avelocity:
                #send IR commands for advance until desired input is reached
                while ivara < avelocity:
                    StormTest.PressButton(ADVANCE)
                    StormTest.WaitSec(1)
                    ivara += 1
                #print out test case with corresponding key and value pair
                SThelperNew.takeScreenshot('Advance test' + str(key), 'Advance forward ' + str(value) + ' at ' + str(key) + ' input.' )
                #break out of loop to save computation time
                break
    except:
        SThelperNew.takeScreenshot('No Advance', 'Valid input given but advance did not occur, check main body of advance function')
        return
<<<<<<< HEAD
#Simple replay function, pass TRUE or FALSE if you want the screenshot taken as well
def replayfeed(takeShot):
    if takeShot != TRUE:
        StormTest.PressButton(REPLAY)
        StormTest.WaitSec(3)
    else:
        StormTest.PressButton(REPLAY)
        StormTest.WaitSec(3)
        SThelperNew.takeScreenshot('Replay test', 'Feed is replayed')
#open guide helper function, simply call it like so openguide()
def openguide():
    StormTest.PressButton(GUIDE)
    StormTest.WaitSec(3)
    SThelperNew.takeScreenshot('Guide Test', 'Guide UI Elements appear as BAU')
#change to user specified CHANNEL
def changechannel(cnumber):
    maxchannel = 9999
    try:
        if cnumber > maxchannel: cnumber = maxchannel
        StormTest.PressButton(cnumber)
        StormTest.PressButton(ENTER)
        StormTest.WaitSec(3)
        SThelperNew.takeScreenshot('Tune to channel' + str(cnumber),'Tuned to channel ' + str(cnumber))
    except:
        SThelperNew.takeScreenshot('Change Channel', 'Invalid channel given, input correct channel (1-9999)')
        return
#########################################################
#############<><><> HELPER FUNCTIONS <><><><>############
#########################################################

def test():
    print TEST_NAME, '\n'

#########################################################
###<><><> SCRIPT EDITING AREA BELOW THIS LINE <><><><>###
#########################################################
# Syntax for sending an IR_Conmmand:	StormTest.PressButton(<IR_COMMAND_NAME>)
# Syntax for wait time:     		   	StormTest.WaitSec(<Positive_Integer>)
# Syntax for creating Step/Screenshot:	SThelperNew.takeScreenshot('<Step Name>', '<Verification(S)>')

    #Wake the boxes being used before starting any tests.
    wakebox()
    pausefeed()
    StormTest.WaitSec(300)
    playfeed()
    advance(3)


#########################################################
###<><><> SCRIPT EDITING AREA ABOVE THIS LINE <><><><>###
#########################################################


    return (StormTest.TM.PASS)


#def runTest(testIDinput=0, slotInput=SLOT, rackInput=RACK):
def runTest():

    SThelperNew.setUpTestEnvironment()
    result = SThelperNew.runAllPorts(test, sys.argv)
    SThelperNew.endTestEnvironment(result)

if __name__ == '__main__':
    runTest()
    StormTest.ReturnTestResult(test())
