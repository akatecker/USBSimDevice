""" =============================================================================================
HID SimConnect interactions
=================================================================================================
v0.1 / 14.05.2024 (cc) AkaTecker
v0.2 / 18.05.2024 refactor
v0.3 / 20.05.2024 Added MFT Chalange Disk, updated Velone
v0.4 / 21.05.2024 Updated Saitek Autopilot Panel
v0.5 / 24.05.2024 Updated Contour Pro
v0.6 / 02.06.2024 Added CHflight

Sample application using USBSimDevice to configure different non-standard USB devices for
use with MSFS 2020 interacting through pysimconnect.
=============================================================================================="""

from USBSimDevice import USBSimDevice, METH, IO
from simconnect import SimConnect, PERIOD_VISUAL_FRAME
from time import sleep, time
import argparse

####################################
##### Hardware Definition here #####
####################################

# Set command line options to switch on supported devices
parser = argparse.ArgumentParser(prog='USBSimActions')

parser.add_argument('-Contour', dest='Contour', action='store_true', help='Use Contour Pro as input device for Garmin G1000 system')
parser.add_argument('-Velone', dest='Velone', action='store_true',  help='Define annunciator lights at Velocity One Pro flightstick')
parser.add_argument('-SaitekAP', dest='SaitekAP', action='store_true', help='Use Saitek / Logitech Multipanel to control and display autopilot')
parser.add_argument('-SaitekSW', dest='SaitekSW', action='store_true', help='Define actions for Saitek Switchpanel')
parser.add_argument('-MFTChallange', dest='MFTChallange', action='store_true', help='Use MFT Challange Disk to controll aileron and elevator by balancing')
parser.add_argument('-CHflight', dest='CHflight', action='store_true', help='Use buttons and hat on analog joystick')

Activate = vars(parser.parse_args())

# Default values if no option is set
if not any(Activate.values()):  
    Activate["Contour"] = True
    Activate["Velone"] = True
    Activate["SaitekAP"] = True

print(Activate)

# Hardwaredefinition Contour

if Activate.get("Contour"):

    def ActionContour(self):
        # process buttons
        ins = self.input_ios()
        if ins["Index"]: sc.send_event('MobiFlight.AS1000_PFD_DIRECTTO')
        if ins["Middle"]: sc.send_event('MobiFlight.AS1000_PFD_ENT_Push')
        if ins["Ring"]: sc.send_event('MobiFlight.AS1000_PFD_CLR')
        if ins["Thumb"]: sc.send_event('MobiFlight.AS1000_PFD_FMS_Lower_DEC')
        if ins["Pinky"]: sc.send_event('MobiFlight.AS1000_PFD_FMS_Lower_INC')
        if ins["Inner"]:
            if ins["Inner"]-self.inner_prev < -2:
                sc.send_event('MobiFlight.AS1000_PFD_FMS_Upper_INC')
            elif ins["Inner"]-self.inner_prev < 0:
                sc.send_event('MobiFlight.AS1000_PFD_FMS_Upper_DEC')
            elif ins["Inner"]-self.inner_prev > 2:
                sc.send_event('MobiFlight.AS1000_PFD_FMS_Upper_DEC')
            elif ins["Inner"]-self.inner_prev > 0:
                sc.send_event('MobiFlight.AS1000_PFD_FMS_Upper_INC')
            self.inner_prev = ins["Inner"]
        if ins["Outer"]:
            if ins["Outer"]>0 and ins["Outer"]>self.outer_prev:
                sc.send_event('MobiFlight.AS1000_MFD_RANGE_DEC')
            elif ins["Outer"]<0 and ins["Outer"]<self.outer_prev:
                sc.send_event('MobiFlight.AS1000_MFD_RANGE_INC')
            self.outer_prev = ins["Outer"]
        
    Contour = USBSimDevice(0x0b33, 0x0020, 0, METH.READ)
    Contour.set_inputs([IO("Outer", 0,-7), IO("Inner", 1,8), IO("Thumb",3,4), IO("Index",3,5), IO("Middle",3,6), IO("Ring",3,7), IO("Pinky",4,0)])
    Contour.set_actions(ActionContour)
    # Instance Variables for previous position of the scroll wheels
    Contour.inner_prev = 0
    Contour.outer_prev = 0

# Hardwaredefinition Turtle Beach VelocitiyOne Flight Pro

VELONE_OFF, VELONE_RED, VELONE_GREEN, VELONE_YELLOW, VELONE_BLUE, VELONE_WHITE = 1, 2, 3, 4, 5, 6

if Activate.get("Velone"):

    def ActionVelone(self):
        if simvarsChanged:
            # Landing Gear
            if simvars.simdata['GEAR LEFT POSITION']>0.95 and simvars.simdata['GEAR RIGHT POSITION']>0.95 and simvars.simdata['GEAR CENTER POSITION']>0.95:
                self.output_io("X2Y1", VELONE_GREEN)
                self.blink_off("X2Y1")
            elif simvars.simdata['GEAR LEFT POSITION']<0.05 and simvars.simdata['GEAR RIGHT POSITION']<0.05 and simvars.simdata['GEAR CENTER POSITION']<0.05:
                self.output_io("X2Y1", VELONE_OFF)
                self.blink_off("X2Y1")
            else:
                self.output_io("X2Y1", VELONE_YELLOW)
                self.blink_on("X2Y1",VELONE_RED)
            # Autopilot
            if simvars.simdata["AUTOPILOT MASTER"]:
                self.output_io("X1Y3", VELONE_GREEN)
            else:
                self.output_io("X1Y3", VELONE_OFF)
            # Parking Brakes
            if simvars.simdata["BRAKE PARKING INDICATOR"]:
                self.output_io("X1Y1", VELONE_RED)
            else:
                self.output_io("X1Y1", VELONE_OFF)
            # Spoilers
            if simvars.simdata['SPOILERS LEFT POSITION']>0.10 and simvars.simdata['SPOILERS RIGHT POSITION']>0.10:
                self.output_io("X1Y2", VELONE_YELLOW)
            else:
                self.output_io("X1Y2", VELONE_OFF)  
            # Stall Warning
            if simvars.simdata['STALL WARNING']:
                self.output_io("X2Y2", VELONE_RED)
            else:
                self.output_io("X2Y2", VELONE_OFF)

    Velone = USBSimDevice(0x10f5, 0x7001, 0, METH.WRITE)
    Velone.set_outputs([IO("X1Y1",  6,8), IO("X2Y1",  8,8), IO("X1Y2", 10,8), IO("X2Y2", 12,8), IO("X1Y3", 14,8), IO("X2Y3", 16,8),
                        IO("X3Y1", 18,8), IO("X4Y1", 20,8), IO("X3Y2", 22,8), IO("X4Y2", 24,8), IO("X3Y3", 26,8), IO("X4Y3", 28,8)])
    Velone.set_actions(ActionVelone)
    Velone.set_simvars(['GEAR RIGHT POSITION', 'GEAR LEFT POSITION', 'GEAR CENTER POSITION', 'AUTOPILOT MASTER', 'BRAKE PARKING INDICATOR',
                        'SPOILERS LEFT POSITION', 'SPOILERS RIGHT POSITION', 'STALL WARNING'])
    Velone.output([ 3,  0,  0, 25,  1,  0,  1,  1,  1,  2,  1,  3,  1,  4,  1,  5,  1,  6,  1,  7,  1,  8,  1,  9,  1, 10,  1, 11,  1])

# Hardwaredefinition MFT Challange Disk

if Activate.get("MFTChallange"):
    
    DUmin, DUmax, DUcen = 400, 600, 500 # range down up before calibration
    RLmin, RLmax, RLcen = 300, 500, 400 # range right left before calibration
    DUfac, RLfac = 100, 100 # linear factor for disk->axis 
    MFTChallangeCalibMode = True
    MFTChallangeCalibDelay = 15 # calibrate during the first seconds
    MFTChallangeCalibTime = int(time())

    def ActionMFTChallange(self):
        global DUmin, DUmax, DUcen, RLmin, RLmax, RLcen, MFTChallangeCalibMode, MFTChallangeCalibTime, DUfac, RLfac
        ins = self.input_ios()
        # If in calibration mode (first seconds) adjust min and max settings)
        if MFTChallangeCalibMode:
            for i in ins:
                 if i == 'DU':
                     DUmin = min(DUmin,ins['DU'])
                     DUmax = max(DUmax,ins['DU'])
                 if i == 'RL':
                     RLmin = min(RLmin,ins['RL'])
                     RLmax = max(RLmax,ins['RL'])
            if MFTChallangeCalibTime + MFTChallangeCalibDelay < int(time()):
                 MFTChallangeCalibMode = False
                 DUcen = int((DUmin+DUmax)/2)
                 DUfac = 16000/(DUmax-DUmin)
                 RLcen = int((RLmin+RLmax)/2)
                 RLfac = 16000/(RLmax-RLmin)
                 print("Challange Disk calibrated!")
        # Continue with regular tasks
        for i in ins:
            if i=="DU":
                sc.send_event('ELEVATOR_SET', int((ins[i]-DUcen)*DUfac))
            if i=="RL":
                sc.send_event('AILERON_SET', int((ins[i]-RLcen)*RLfac))
                
    MFTChallange = USBSimDevice(0x17b5, 0x0010, 0, METH.READ_LAST)
    MFTChallange.set_inputs([IO("DU", 0,16), IO("RL", 2,16)])
    MFTChallange.set_actions(ActionMFTChallange)

# Hardwaredefinition Saitek Autopilot Panel

if Activate.get("SaitekAP"):

    def saitek_num(value, digits=2):
        # Format value for display on Saitek LCD screen
        value = round(value/10**digits)*10**digits
        stream = bytearray(str(value), encoding='utf-8')
        formated = [0x0f,0x0f,0x0f,0x0f,0x0f]
        streamlen = len(stream)-1
        for i in range(streamlen+1):
            if stream[streamlen-i]==45:
                formated[4-i]=0xde
            else:
                formated[4-i]=stream[streamlen-i]-48
        return (formated)
    
    def ActionSaitekAP(self):
        global simvarsChanged
        # process buttons
        ins = self.input_ios()
        if ins["DispALT"]: self.select=0;simvarsChanged=True
        if ins["DispVS"]: self.select=1;simvarsChanged=True
        if ins["DispIAS"]: self.select=2;simvarsChanged=True
        if ins["DispHDG"]: self.select=3;simvarsChanged=True
        if ins["DispCRS"]: self.select=4;simvarsChanged=True
        if ins["B0"]: sc.send_event('AUTOPILOT_DISENGAGE_SET', 0);sc.send_event('AP_MASTER')
        if ins["B1"]: sc.send_event('AP_HDG_HOLD')
        if ins["B2"]: sc.send_event('AP_NAV1_HOLD')
        if ins["B3"]: sc.send_event('AP_APR_HOLD')
        if ins["B4"]: sc.send_event('AP_ALT_HOLD')
        if ins["B5"]: sc.send_event('AP_VS_HOLD')
        if ins["B6"]: pass # sc.send_event('')
        if ins["B7"]: pass # sc.send_event('')
        if ins["FlUP"]: sc.send_event('FLAPS_DECR')
        if ins["FlDN"]: sc.send_event('FLAPS_INCR')
        if ins["TrUP"]: sc.send_event('AP_VS_VAR_INC')
        if ins["TrDN"]: sc.send_event('AP_VS_VAR_DEC')
        if ins["TurnCW"] and (self.select==0 or self.select==1): sc.send_event('AP_ALT_VAR_INC')
        if ins["TurnCCW"] and (self.select==0 or self.select==1): sc.send_event('AP_ALT_VAR_DEC')
        if ins["TurnCW"] and self.select==3: sc.send_event('HEADING_BUG_INC')
        if ins["TurnCCW"] and self.select==3: sc.send_event('HEADING_BUG_DEC')
        # process simvar inputs to led and display
        if simvarsChanged:
            # Autopilot Master
            if simvars.simdata["AUTOPILOT MASTER"]: self.output_io("Led0", 1)
            else: self.output_io("Led0", 0)
            # Heading Mode
            if simvars.simdata["AUTOPILOT HEADING LOCK"]: self.output_io("Led1", 1)
            else: self.output_io("Led1", 0)
            # Nav Mode
            if simvars.simdata["AUTOPILOT NAV1 LOCK"]: self.output_io("Led2", 1)
            else: self.output_io("Led2", 0)
            # Approach Mode
            if simvars.simdata["AUTOPILOT APPROACH HOLD"]:
                self.output_io("Led3", 1)
                if simvars.simdata["AUTOPILOT APPROACH CAPTURED"]:
                    self.blink_off("LED3")
                else:
                    self.blink_on("LED3", 0)
            else:
                self.output_io("Led3", 0)
                self.blink_off("LED3")
            # Altitude Hold Mode
            if simvars.simdata["AUTOPILOT ALTITUDE LOCK"]: self.output_io("Led4", 1)
            else: self.output_io("Led4", 0)
            # Altitude Arm
            if simvars.simdata["AUTOPILOT ALTITUDE ARM"]: self.output_io("Led4", 1)
            else: self.output_io("Led4", 0)
            # Vertical Speed engage
            if simvars.simdata["AUTOPILOT VERTICAL HOLD"]: self.output_io("Led5", 1)
            else: self.output_io("Led5", 0)
            # default output empty display
            self.output([0x0f,0x0f,0x0f,0x0f,0x0f],1)
            self.output([0x0f,0x0f,0x0f,0x0f,0x0f],5)
            # Vertical Speed Display
            if simvars.simdata["AUTOPILOT VERTICAL HOLD"] and (self.select==0 or self.select==1):
                self.output(saitek_num(simvars.simdata["AUTOPILOT VERTICAL HOLD VAR"]),5)
            # Altitude Display
            if self.select==0 or self.select==1:
                self.output(saitek_num(simvars.simdata["AUTOPILOT ALTITUDE LOCK VAR"]),1)
            # Heading Display
            if self.select==3:
                self.output(saitek_num(simvars.simdata["AUTOPILOT HEADING LOCK DIR"],0),1)

    SaitekAP = USBSimDevice(0x06a3, 0x0d06, 0, METH.READ | METH.WRITE_FEATURE)
    SaitekAP.set_inputs( [IO("DispALT", 0,0), IO("DispVS",  0,1), IO("DispIAS", 0,2), IO("DispHDG", 0,3), IO("DispCRS", 0,4), IO("TurnCW", 0,5), IO("TurnCCW", 0,6), IO("B0", 0,7),
                          IO("B1",      1,0), IO("B2",      1,1), IO("B3",      1,2), IO("B4",      1,3), IO("B5",      1,4), IO("B6",     1,5), IO("B7",      1,6), IO("Arm", 1,7),
                          IO("FlUP",    2,0), IO("FlDN",    2,1), IO("TrUP",    2,2), IO("TrDN",    2,3)])
    SaitekAP.set_outputs([IO("Led0",  11,0), IO("Led1", 11,1), IO("Led2", 11,2), IO("Led3", 11,3), IO("Led4", 11,4), IO("Led5", 11,5), IO("Led6", 11,6), IO("Led7", 11,7)])
    SaitekAP.set_actions(ActionSaitekAP)
    SaitekAP.set_simvars(['AUTOPILOT MASTER', 'AUTOPILOT HEADING LOCK', 'AUTOPILOT NAV1 LOCK', 'AUTOPILOT APPROACH HOLD',
                          'AUTOPILOT ALTITUDE LOCK', 'AUTOPILOT ALTITUDE ARM', 'AUTOPILOT VERTICAL HOLD', 'AUTOPILOT VERTICAL HOLD VAR',
                          'AUTOPILOT ALTITUDE LOCK VAR', 'AUTOPILOT HEADING LOCK DIR', 'AUTOPILOT APPROACH CAPTURED'])
    SaitekAP.output([1, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,  0, 0])
    SaitekAP.select = 0 

# Hardwaredefinition Saitek Switch Panel

if Activate.get("SaitekSW"):

    def ActionSaitekSW(self):
        pass

    SaitekSW = USBSimDevice(0x06a3, 0x0d05, 0,METH.READ | METH.WRITE)
    SaitekSW.set_outputs([IO("Green N", 0,0), IO("Green L", 0,1), IO("Green R",  0,2), IO("Red N",     0,3), IO("Red L",   0,4), IO("Red R", 0,5)])
    SaitekSW.set_inputs([ IO("BAT",     0,0), IO("ALT",     0,1), IO("AVIONICS", 0,2), IO("FUEL",      0,3), IO("DE-ICE",  0,4), IO("PITOT", 0,5), IO("COWL", 0,6), IO("PANEL", 0,7),
                          IO("BEACON",  1,0), IO("NAV",     1,1), IO("STROBE",   1,2), IO("TAXI",      1,3), IO("LANDING", 1,4), IO("OFF",   1,5), IO("R",    1,6), IO("L",     1,7),
                          IO("BOTH",    2,0), IO("START",   2,1), IO("GEAR UP",  2,2), IO("GEAR DOWN", 2,3)])
    SaitekSW.set_actions(ActionSaitekSW)
    SaitekSW.output([ 7])

# Hardwaredefinition CH Flightstick Gameport using noname converter

if Activate.get("CHflight"):

    def ActionCHflight(self):
        # process buttons
        ins = self.input_ios()
        if ins["Buttons"]==1:    pass # B1
        elif ins["Buttons"]==4:  pass # B2
        elif ins["Buttons"]==5:  pass # B3
        elif ins["Buttons"]==9:  pass # B4
        elif ins["Buttons"]==8:  pass # B5
        elif ins["Buttons"]==2:  pass # B6
        elif ins["Buttons"]==14: pass # Hat 1 Up
        elif ins["Buttons"]==10: pass # Hat 1 Right
        elif ins["Buttons"]==6:  pass # Hat 1 Down
        elif ins["Buttons"]==12: pass # Hat 1 Left
        elif ins["Buttons"]==15: pass # Hat 2 Up
        elif ins["Buttons"]==11: pass # Hat 2 Right
        elif ins["Buttons"]==7:  pass # Hat 2 Down
        elif ins["Buttons"]==3:  pass # Hat 2 Left
        # set axis
        sc.send_event('ELEVATOR_SET', int((ins["Elevator"]-60)*260))
        sc.send_event('AILERON_SET', int((ins["Aileron"]-80)*220))
    
    CHflight = USBSimDevice(0x079D, 0x0201, 0, METH.READ)
    CHflight.set_inputs([IO("Aileron", 0, 8), IO("Elevator", 1, 8), IO("Throttle", 5, 8)], IO("Buttons", 4, 8))
    CHflight.set_actions(ActionCHflight)

# Hardwaredefinition add your Hardware here

'''
if Activate.get("XXX"):

    def ActionXXX(self):
        pass
    
    XXX = USBSimDevice(0x17b5, 0x0010, 0,METH.READ)
    XXX.set_inputs([IO("LR", 0,16), IO("UD", 2,16)])
    XXX.set_actions(ActionXXX)
'''

#######################
##### Main Loop #######
#######################

def openSimConnect():
    global simvars, sc
    try:
        sc = SimConnect()
        simvars = sc.subscribe_simdata(USBSimDevice.Simvars, period=PERIOD_VISUAL_FRAME, interval=10)
        return True
    except:
        return False

# Try to connect to SimConnect
while not openSimConnect():
    pass
# Main        
while True:
    
    # Get Simconnect Data
    latest = simvars.simdata.latest()
    try:
        # Get fresh Sim Data
        sc.receive(timeout_seconds=0.01)
    except:
        pass
    simvarsChanged = (len(simvars.simdata.changedsince(latest)) != 0)
    # USB io is faster than Simconnect, therefor repeat 5 times
    for i in range(5):
        # Process USB devices one by one
        for worker in USBSimDevice.Workers:
            worker.update()
            worker.actions()
        # Minimum wait time
        sleep(0.001)