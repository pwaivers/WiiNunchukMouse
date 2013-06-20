# Import the required libraries for this script
import math, string, time, serial, os, AppKit
from Quartz.CoreGraphics import CGEventCreateMouseEvent
from Quartz.CoreGraphics import CGEventPost
from Quartz.CoreGraphics import kCGEventMouseMoved
from Quartz.CoreGraphics import kCGEventLeftMouseDown
from Quartz.CoreGraphics import kCGEventLeftMouseDown
from Quartz.CoreGraphics import kCGEventLeftMouseUp
from Quartz.CoreGraphics import kCGEventRightMouseDown
from Quartz.CoreGraphics import kCGEventRightMouseUp
from Quartz.CoreGraphics import kCGMouseButtonLeft
from Quartz.CoreGraphics import kCGHIDEventTap
from Quartz.CoreGraphics import CGEventCreateScrollWheelEvent

# Define the Mouse Click events
def mouseEvent(type, posx, posy):
        theEvent = CGEventCreateMouseEvent(
                    None, 
                    type, 
                    (posx,posy), 
                    kCGMouseButtonLeft)
        CGEventPost(kCGHIDEventTap, theEvent)

def mousemove(posx,posy):
        mouseEvent(kCGEventMouseMoved, posx,posy);

def mouseclick(posx,posy):
        # uncomment this line if you want to force the mouse 
        # to MOVE to the click location first (I found it was not necessary).
        #mouseEvent(kCGEventMouseMoved, posx,posy);
        mouseEvent(kCGEventLeftMouseDown, posx,posy);
        mouseEvent(kCGEventLeftMouseUp, posx,posy);

def clamp(my_value, min_value, max_value):
    return max(min(my_value, max_value), min_value)

# The port to which your Arduino board is connected
port = '/dev/tty.usbmodem1411'

# Invert y-axis (True/False)
invertY = False

# The cursor speed
cursorSpeed = 20

# The baudrate of the Arduino program
baudrate = 19200

# Variables indicating whether the mouse buttons are pressed or not
leftDown = False
rightDown = False
locx = 100
locy = 100

# Variables used for backSpace
leaningLeft = False
leaningLeftTimer = 0
leaningLeftTimeNeeded = 1000 # in milliseconds

# Variables indicating the center position (no movement) of the controller
midAccelX = 530 # Accelerometer X
midAccelY = 510 # Accelerometer Y
midAnalogX = 126 # Analog X
midAnalogY = 128 # Analog Y

# Variables for scrolling
scrollingDown = False
scrollingUp = False
scrollspeed = 2
scrollsensitivity = 20

# Varaibles for nuetral position (for scrolling)
nuetraly = 120.0
nymax = 135
nymin = 100
driftspeed = 0.002

# get the dimensions of the monitors
# returns a tuple if there is more than one monitor
dimensions = [(screen.frame().size.width, screen.frame().size.height, screen.frame().origin.x, screen.frame().origin.y)
    for screen in AppKit.NSScreen.screens()]
height = dimensions[0][1]
width = dimensions[0][0]

# Connect to the serial port
ser = serial.Serial(port, baudrate, timeout = 1)

# Wait 1s for things to stabilize
time.sleep(1)

# While the serial port is open
while ser.isOpen():


    line = ser.readline()

    # Strip the ending (\r\n)
    line = string.strip(line, '\r\n')

    # Split the string into an array containing the data from the Wii Nunchuk
    line = string.split(line, ' ')

    
    

    # start logging here


    try:
        # x and y coordinates of the joystick
        xcoor = float(line[0]) - 126
        xcoor = 0 if xcoor < 5 and xcoor > -5 else xcoor 	#avoid creeping
        xcoor = xcoor / 2 if xcoor < 30 and xcoor > -30 else xcoor 	#create finer control near the center of the joystick

        ycoor = float(line[1]) - midAnalogY
        yvoor = 0 if ycoor < 5 and ycoor > -5 else ycoor 
        ycoor = ycoor / 2 if ycoor < 30 and ycoor > -30 else ycoor 

        zbut = int(line[5])
        cbut = int(line[6])

        accx = float(line[2])
        accy = float(line[3])

    except IndexError:
        print "Out of Index Exception"
        continue
    except Exception as e:
        print e
        continue

    # "drift" the nuetral position
    if (accy < nymax) and (accy >  nymin):
        nuetraly = nuetraly * ( 1 - driftspeed ) + accy * driftspeed

    # lean nunchuk forward to scroll up
    if accy < ( nuetraly - scrollsensitivity ):
        event = CGEventCreateScrollWheelEvent(None, 0, 1, (accy - (nuetraly - scrollsensitivity ) ) * scrollspeed)
        CGEventPost(kCGHIDEventTap, event)
    # lean nunchuk backwards to scroll down
    if accy > ( nuetraly + scrollsensitivity ):
        event = CGEventCreateScrollWheelEvent(None, 0, 1, (accy - ( nuetraly + scrollsensitivity )) * scrollspeed)
        CGEventPost(kCGHIDEventTap, event)

    # exit the program
    if (zbut == 1) and (cbut == 1):
        break
    locx = locx + xcoor / 2
    locy = locy - ycoor / 2 # the direction of the y coordinate is inverted of the screen
        

    # clamp the x and y locations
    locx = clamp(locx, 0, width - 1)
    locy = clamp(locy, 0, height - 1)

    mousemove(locx, locy)

    # Left mouse click
    if (zbut == 1) and (leftDown == False):
        mouseEvent(kCGEventLeftMouseDown, locx, locy);
    	leftDown = True
    if (zbut == 0) and (leftDown == True):
        mouseEvent(kCGEventLeftMouseUp, locx, locy);
    	leftDown = False
    	print "Left button event"

    # Right mouse click
    cbut = int(line[6])
    if (cbut == 1) and (zbut == 0) and (rightDown == False):
        mouseEvent(kCGEventRightMouseDown, locx, locy);
    	rightDown = True
    if (cbut == 0) and (rightDown == True):
        mouseEvent(kCGEventRightMouseUp, locx, locy);
    	rightDown = False
    	print "Right button event"


    # backSpace by leaning the nunchuk left
    if (accx < 8) and (leaningLeft == False):
        leaningLeft = True
        leaningLeftTimer = time.time() * 1000
    if (accx >= 115) and (leaningLeft == True):
        leaningLeft = False
        # if the left lean was quick ( < 1s), do backspace
        if (time.time() * 1000) - leaningLeftTimer < leaningLeftTimeNeeded: 
            cmd = """
            osascript -e 'tell application "System Events" to key code 51' 
            """
            os.system(cmd)
            print "BackSpace"

ser.close()