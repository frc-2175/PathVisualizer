from tkinter import *
from math import *
import threading
from networktables import NetworkTables

# To get this application to function with Smart Dashboard, uncomment anything with the heading "Smart Dashboard ..."

# Smart Dashboard things

# cond = threading.Condition()
# notified = [False]

# def connectionListener(connected, info):
#     print(info, '; Connected=%s' % connected)
#     with cond:
#         notified[0] = True
#         cond.notify()

# NetworkTables.initialize(server='10.21.75.2')
# NetworkTables.addConnectionListener(connectionListener, immediateNotify = True)

# with cond:
#     print("Waiting")
#     if not notified[0]:
#         cond.wait()

# print("Connected!")
# table = NetworkTables.getTable('SmartDashboard')
# valuesTable = table.getSubTable('Values')

# Constants

FRAME_TIME = 20
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 800
AXIS_WIDTH = 2
AXIS_PADDING = 20
EXAMPLE_DATA = [
    [0.0, 0.0],
    [0.2886718180492783, 3.1578947368421053],
    [1.1126986441172182, 6.315789473684211],
    [2.409097536083977, 9.473684210526315],
    [4.114885551829713, 12.631578947368421],
    [6.167079749234581, 15.789473684210527],
    [8.502697186178741, 18.94736842105263],
    [11.058754920542352, 22.105263157894733],
    [13.772270010205569, 25.263157894736842],
    [16.580259513048546, 28.421052631578945],
    [19.419740486951447, 31.578947368421055],
    [22.227729989794426, 34.73684210526316],
    [24.94124507945764, 37.89473684210526],
    [27.497302813821264, 41.05263157894737],
    [29.83292025076541, 44.210526315789465],
    [31.8851144481703, 47.368421052631575],
    [33.590902463916024, 50.526315789473685],
    [34.88730135588278, 53.68421052631579],
    [35.71132818195072, 56.84210526315789],
    [36.0, 60.0]
]

# Smart Dashboard data for the path
PATH_POINTS = []
# x_coords = valuesTable.getNumberArray("PathXCoords", [])
# y_coords = valuesTable.getNumberArray("PathYCoords", [])
# for i in range(min(len(x_coords), len(y_coords))):
#     PATH_POINTS.append([x_coords[i], y_coords[i]])

X_SCALE = 36 
Y_SCALE = 60
GRIDLINE_WIDTH = (CANVAS_WIDTH - AXIS_PADDING) / X_SCALE
GRIDLINE_HEIGHT = (CANVAS_HEIGHT - AXIS_PADDING) / Y_SCALE
POINT_RADIUS = 5
ROBOT_LINE_LENGTH = 100

# Connfigure window

master = Tk()
master.title("Visualizer")
w = Canvas(master, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
w.pack(expand=YES, fill=BOTH)
w.config(background="#FFFFFF")

def draw_axes():
    "Draws the axes on the window with specified padding in constants list"
    w.create_line(AXIS_PADDING, 0, AXIS_PADDING, CANVAS_HEIGHT, width=AXIS_WIDTH)
    w.create_line(0, CANVAS_HEIGHT - AXIS_PADDING, CANVAS_WIDTH, CANVAS_HEIGHT - AXIS_PADDING, width=AXIS_WIDTH)

def draw_grid():
    "Draws a grid with the space between gridlines being one graph unit"
    offset = AXIS_PADDING + GRIDLINE_WIDTH
    for i in range(0, X_SCALE):
        w.create_line(offset, 0, offset, CANVAS_HEIGHT)
        offset += GRIDLINE_WIDTH
    offset = (CANVAS_HEIGHT - AXIS_PADDING) - GRIDLINE_HEIGHT
    for i in range(0, Y_SCALE):
        w.create_line(0, offset, CANVAS_WIDTH, offset)
        offset -= GRIDLINE_HEIGHT
    
def plot_point(x, y):
    "Plots a point on the graph with graph coordinates x and y"
    x_coord = AXIS_PADDING + x * GRIDLINE_WIDTH
    y_coord = CANVAS_HEIGHT - (AXIS_PADDING + y * GRIDLINE_HEIGHT)
    w.create_oval(x_coord + POINT_RADIUS, y_coord + POINT_RADIUS, x_coord - POINT_RADIUS, y_coord - POINT_RADIUS, fill="#000000")

def plot_data(data):
    "Plots the data specified, where data is a list of length-two number lists (a list of points)"
    for point in data:
        plot_point(point[0], point[1])

def draw_robot(robotx, roboty, robotzRotation):
    "Draw two intersecting lines at robotx and roboty with a rotation of robotzRotation degrees"
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
    draw_axes()
    draw_grid()
    plot_data(EXAMPLE_DATA)
    # Smart Dashboard stuff that draws the position and rotation of the robot
    # draw_robot(valuesTable.getNumber("PositionX", 0), valuesTable.getNumber("PositionY", 0), valuesTable.getNumber("Gyro", 0))
    master.after(FRAME_TIME, draw)

master.after(FRAME_TIME, draw)

master.lift()
master.call('wm', 'attributes', '.', '-topmost', '1')

mainloop()
