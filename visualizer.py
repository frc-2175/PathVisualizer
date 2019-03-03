from tkinter import *
from math import *
import threading
from networktables import NetworkTables

# To get this application to function with Smart Dashboard, uncomment anything with the heading "Smart Dashboard ..."

# Smart Dashboard things

cond = threading.Condition()
notified = [False]

def connectionListener(connected, info):
     print(info, '; Connected=%s' % connected)
     with cond:
        notified[0] = True
        cond.notify()

NetworkTables.initialize(server='10.21.75.2')
NetworkTables.addConnectionListener(connectionListener, immediateNotify = True)

with cond:
    print("Waiting")
    if not notified[0]:
        cond.wait()

print("Connected!")
table = NetworkTables.getTable('SmartDashboard')
valuesTable = table.getSubTable('Values')

"""
Things to do:
1. Make path points update during the main loop so that we can see in real time with a vision target [have something... probably won't work & will have to look at]
2. Add a few "buffer" gridlines beyond end of path for X & Y so the real robot never goes off the screen... [should be fixed]
3. Change the Quadrant 1 & Quadrant 2 feature to scale correctly for both quadrants individually
"""

# Constants and variables
FRAME_TIME = 20
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 800
AXIS_WIDTH = 2
AXIS_PADDING = 20
EXAMPLE_DATA = [
    [0.0, 0.0],
    [2.0, 1.5],
    [4.0, 1.5]
]
x_coords = []
y_coords = []
PATH_POINTS = []
X_SCALE = 0
Y_SCALE = 0
GRIDLINE_WIDTH = 0
GRIDLINE_HEIGHT = 0
QUADRANT_1 = False
QUADRANT_2 = False

"""
for point in EXAMPLE_DATA:
    x_coords.append(point[0])
    y_coords.append(point[1])
"""

POINT_RADIUS = 5
ROBOT_LINE_LENGTH = 100

# Configure window

master = Tk()
master.title("Visualizer")
w = Canvas(master, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
w.pack(expand=YES, fill=BOTH)
w.config(background="#FFFFFF")

def generate_path(x_coords, y_coords):
    QUADRANT_1 = False
    QUADRANT_2 = False
    for i in range(min(len(x_coords), len(y_coords))):
        PATH_POINTS.append([x_coords[i], y_coords[i]])
        X_SCALE = int(abs(max(x_coords, key=abs))) + 1
        Y_SCALE = int(max(y_coords)) + 1
    X_SCALE = int(X_SCALE * 1.20)
    Y_SCALE = int(Y_SCALE * 1.20)
    if(min(x_coords) < 0):
        QUADRANT_2 = True
    if(max(x_coords) > 0):
        QUADRANT_1 = True
    if(QUADRANT_1 and QUADRANT_2):
        X_SCALE *= 2
    GRIDLINE_WIDTH = (CANVAS_WIDTH - AXIS_PADDING) / X_SCALE
    GRIDLINE_HEIGHT = (CANVAS_HEIGHT - AXIS_PADDING) / Y_SCALE

def draw_axes():
    "Draws the axes on the window with specified padding in constants list"
    w.create_line(0, CANVAS_HEIGHT - AXIS_PADDING, CANVAS_WIDTH, CANVAS_HEIGHT - AXIS_PADDING, width=AXIS_WIDTH)
    if(QUADRANT_1 and QUADRANT_2):
        w.create_line(CANVAS_WIDTH / 2.0, 0, CANVAS_WIDTH / 2.0, CANVAS_HEIGHT, width=AXIS_WIDTH)
    elif(QUADRANT_1):
        w.create_line(AXIS_PADDING, 0, AXIS_PADDING, CANVAS_HEIGHT, width=AXIS_WIDTH)
    else:
        w.create_line(CANVAS_WIDTH - AXIS_PADDING, 0, CANVAS_WIDTH - AXIS_PADDING, CANVAS_HEIGHT, width=AXIS_WIDTH)

def draw_grid():
    "Draws a grid with the space between gridlines being one graph unit"
    offset = (CANVAS_HEIGHT - AXIS_PADDING) - GRIDLINE_HEIGHT
    for i in range(0, Y_SCALE):
        w.create_line(0, offset, CANVAS_WIDTH, offset)
        offset -= GRIDLINE_HEIGHT
    offset = AXIS_PADDING + GRIDLINE_WIDTH
    if(QUADRANT_1 and QUADRANT_2):
        offset = CANVAS_WIDTH / 2.0
        offset2 = offset
        for i in range(0, X_SCALE):
            w.create_line(offset, 0, offset, CANVAS_HEIGHT)
            offset += GRIDLINE_WIDTH
            w.create_line(offset2, 0, offset2, CANVAS_HEIGHT)
            offset2 -= GRIDLINE_WIDTH
    elif(QUADRANT_1):
        for i in range(0, X_SCALE):
            w.create_line(offset, 0, offset, CANVAS_HEIGHT)
            offset += GRIDLINE_WIDTH
    else:
        offset = 0
        for i in range(0, X_SCALE):
            w.create_line(offset, 0, offset, CANVAS_HEIGHT)
            offset += GRIDLINE_WIDTH

def plot_point(x, y, color):
    "Plots a point on the graph with graph coordinates x and y"
    y_coord = CANVAS_HEIGHT - (AXIS_PADDING + y * GRIDLINE_HEIGHT)
    if(QUADRANT_1 and QUADRANT_2):
        x_coord = (CANVAS_WIDTH / 2) + x * GRIDLINE_WIDTH
    elif(QUADRANT_1):
        x_coord = AXIS_PADDING + x * GRIDLINE_WIDTH
    else:
        x_coord = (CANVAS_WIDTH - AXIS_PADDING) + x * GRIDLINE_WIDTH
    w.create_oval(x_coord + POINT_RADIUS, y_coord + POINT_RADIUS, x_coord - POINT_RADIUS, y_coord - POINT_RADIUS, fill=color)

def plot_data(data):
    "Plots the data specified, where data is a list of length-two number lists (a list of points)"
    for point in data:
        plot_point(point[0], point[1], "#000000")

robotxcoords = []
robotycoords = []

def draw_robot(robotx, roboty, robotzRotation, autoEnabled):
    "Draw two intersecting lines at robotx and roboty with a rotation of robotzRotation degrees"
    if(autoEnabled == True):
        robotxcoords.append(robotx)
        robotycoords.append(roboty)
        for i in range(min(len(robotxcoords), len(robotycoords))):
            plot_point(robotxcoords[i], robotycoords[i],  "#fbff14")
    robotx = AXIS_PADDING + robotx * GRIDLINE_WIDTH
    roboty = CANVAS_HEIGHT - (AXIS_PADDING + roboty * GRIDLINE_HEIGHT)
    x1 = robotx + 0.5 * ROBOT_LINE_LENGTH * sin(radians(robotzRotation))
    y1 = roboty - 0.5 * ROBOT_LINE_LENGTH * cos(radians(robotzRotation))
    x2 = robotx - 0.5 * ROBOT_LINE_LENGTH * sin(radians(robotzRotation))
    y2 = roboty + 0.5 * ROBOT_LINE_LENGTH * cos(radians(robotzRotation))
    w.create_line(x1, y1, x2, y2, width=AXIS_WIDTH, fill="#2cd332")
    x3 = robotx - 0.5 * ROBOT_LINE_LENGTH * cos(radians(robotzRotation))
    y3 = roboty - 0.5 * ROBOT_LINE_LENGTH * sin(radians(robotzRotation))
    x4 = robotx + 0.5 * ROBOT_LINE_LENGTH * cos(radians(robotzRotation))
    y4 = roboty + 0.5 * ROBOT_LINE_LENGTH * sin(radians(robotzRotation))
    w.create_line(x3, y3, x4, y4, width=AXIS_WIDTH, fill="#d23f2c")

def draw():
    "Draws all of the components on the screen and calls itself recursively"
    w.delete('all')
    generate_path(valuesTable.getNumberArray("PathXCoords", []), y_coords = valuesTable.getNumberArray("PathYCoords", []))
    draw_axes()
    draw_grid()
    plot_data(PATH_POINTS)
    # Smart Dashboard stuff that draws the position and rotation of the robot
    draw_robot(valuesTable.getNumber("PositionX", 0), valuesTable.getNumber("PositionY", 0), valuesTable.getNumber("Gyro", 0), valuesTable.getBoolean("AutonomousEnabled", False))
    master.after(FRAME_TIME, draw)

master.after(FRAME_TIME, draw)

master.lift()
master.call('wm', 'attributes', '.', '-topmost', '1')

mainloop()
