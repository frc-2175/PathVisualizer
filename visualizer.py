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
autoPopulateTable = table.getSubTable('AutoPopulate')
visionTable = autoPopulateTable.getSubTable('Vision')
bezierTable = table.getSubTable('Bezier')
purePursuitTable = table.getSubTable('PurePursuitLogging')

# Constants
FRAME_TIME = 20
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 700
AXIS_WIDTH = 2
X_SCALE_MIN = -48
X_SCALE_MAX = 48
Y_SCALE_MIN = -48
Y_SCALE_MAX = 48
GRIDLINE_WIDTH = CANVAS_WIDTH / (X_SCALE_MAX - X_SCALE_MIN)
GRIDLINE_HEIGHT = CANVAS_HEIGHT / (Y_SCALE_MAX - Y_SCALE_MIN)
X_AXIS_POSITION = Y_SCALE_MAX * GRIDLINE_HEIGHT
Y_AXIS_POSITION = abs(X_SCALE_MIN) * GRIDLINE_WIDTH
POINT_RADIUS = 5
ROBOT_LINE_LENGTH = 100

# Configure window
master = Tk()
master.title("Visualizer")
w = Canvas(master, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
w.pack(expand=YES, fill=BOTH)
w.config(background="#FFFFFF")

def draw_axes():
    "Draws the axes on the window with specified padding in constants list"
    w.create_line(0, X_AXIS_POSITION, CANVAS_WIDTH, X_AXIS_POSITION, width=AXIS_WIDTH)
    w.create_line(Y_AXIS_POSITION, 0, Y_AXIS_POSITION, CANVAS_HEIGHT, width=AXIS_WIDTH)

def draw_grid():
    "Draws a grid with the space between gridlines being one graph unit"
    for i in range(0, floor(X_SCALE_MAX)):
        w.create_line(Y_AXIS_POSITION + (i + 1) * GRIDLINE_WIDTH, 0, Y_AXIS_POSITION + (i + 1) * GRIDLINE_WIDTH, CANVAS_HEIGHT, fill="#e8e8e8")
    for i in range(0, floor(abs(X_SCALE_MIN))):
        w.create_line(Y_AXIS_POSITION - (i + 1) * GRIDLINE_WIDTH, 0, Y_AXIS_POSITION - (i + 1) * GRIDLINE_WIDTH, CANVAS_HEIGHT, fill="#e8e8e8")
    for i in range(0, floor(Y_SCALE_MAX)):
        w.create_line(0, X_AXIS_POSITION - (i + 1) * GRIDLINE_HEIGHT, CANVAS_WIDTH, X_AXIS_POSITION - (i + 1) * GRIDLINE_HEIGHT, fill="#e8e8e8")
    for i in range(0, floor(abs(Y_SCALE_MIN))):
        w.create_line(0, X_AXIS_POSITION + (i + 1) * GRIDLINE_HEIGHT, CANVAS_WIDTH, X_AXIS_POSITION + (i + 1) * GRIDLINE_HEIGHT, fill="#e8e8e8")

def plot_point(x, y, color="#000000"):
    "Plots a point on the graph with graph coordinates x and y"
    x_coord, y_coord = graph_to_pixels(x, y)
    w.create_oval(x_coord + POINT_RADIUS, y_coord + POINT_RADIUS, x_coord - POINT_RADIUS, y_coord - POINT_RADIUS, fill=color)

def plot_data(data):
    "Plots the data specified, where data is a list of length-two number lists (a list of points)"
    for point in data:
        plot_point(point[0], point[1])

robot_x_coords = []
robot_y_coords = []

def draw_robot(robotx, roboty, robotzRotation, isAutoEnabled=False):
    "Draw two intersecting lines at robotx and roboty with a rotation of robotzRotation degrees"
    global robot_x_coords
    global robot_y_coords
    if isAutoEnabled:
        print("auto")
        xcoord, ycoord = pixels_to_graph(robotx, roboty)
        robot_x_coords.append(xcoord)
        robot_y_coords.append(ycoord)
        for i in range(min(len(robot_x_coords), len(robot_y_coords))):
            plot_point(robot_x_coords[i], robot_y_coords[i], "#ff0000")
    robotx, roboty = graph_to_pixels(robotx, roboty)
    x1 = robotx + 0.5 * ROBOT_LINE_LENGTH * sin(radians(robotzRotation))
    y1 = roboty - 0.5 * ROBOT_LINE_LENGTH * cos(radians(robotzRotation))
    x2 = robotx - 0.5 * ROBOT_LINE_LENGTH * sin(radians(robotzRotation))
    y2 = roboty + 0.5 * ROBOT_LINE_LENGTH * cos(radians(robotzRotation))
    w.create_line(x1, y1, x2, y2, width=AXIS_WIDTH + 1, fill="#2cd332")
    x3 = robotx - 0.5 * ROBOT_LINE_LENGTH * cos(radians(robotzRotation))
    y3 = roboty - 0.5 * ROBOT_LINE_LENGTH * sin(radians(robotzRotation))
    x4 = robotx + 0.5 * ROBOT_LINE_LENGTH * cos(radians(robotzRotation))
    y4 = roboty + 0.5 * ROBOT_LINE_LENGTH * sin(radians(robotzRotation))
    w.create_line(x3, y3, x4, y4, width=AXIS_WIDTH + 1, fill="#d23f2c")

def graph_to_pixels(graphx, graphy):
    pixelx = Y_AXIS_POSITION + graphx * GRIDLINE_WIDTH    
    pixely = X_AXIS_POSITION - graphy * GRIDLINE_HEIGHT
    return pixelx, pixely

def pixels_to_graph(pixelx, pixely):
    graphx = (pixelx + Y_AXIS_POSITION) / GRIDLINE_WIDTH
    graphy = (pixely - X_AXIS_POSITION) / GRIDLINE_HEIGHT
    return graphx, graphy

def draw():
    "Draws all of the components on the screen and calls itself recursively"
    global GRIDLINE_WIDTH, GRIDLINE_HEIGHT, X_AXIS_POSITION, Y_AXIS_POSITION
    w.delete('all')
    PATH_DATA = []
    x_coords = valuesTable.getNumberArray("PathXCoords", [])
    y_coords = valuesTable.getNumberArray("PathYCoords", [])
    for i in range(min(len(x_coords), len(y_coords))):
        PATH_DATA.append([x_coords[i], y_coords[i]])
    draw_axes()
    draw_grid()
    plot_data(PATH_DATA)
    # Smart Dashboard stuff that draws the position and rotation of the robot
    draw_robot(valuesTable.getNumber("PositionX", 0), valuesTable.getNumber("PositionY", 0), valuesTable.getNumber("Gyro", 0))

    # Draw positions of target corners
    plot_point(visionTable.getNumber("LeftCornerX", 0), visionTable.getNumber("LeftCornerY", 0), '#0000FF')
    plot_point(visionTable.getNumber("RightCornerX", 0), visionTable.getNumber("RightCornerY", 0), '#0000FF')

    # Draw curve handles
    plot_point(bezierTable.getNumber("x1", 0), bezierTable.getNumber("y1", 0), '#FF0000')
    plot_point(bezierTable.getNumber("x2", 0), bezierTable.getNumber("y2", 0), '#FF0000')
    plot_point(bezierTable.getNumber("x3", 0), bezierTable.getNumber("y3", 0), '#FF0000')

    # Draw goal point
    plot_point(purePursuitTable.getNumber('GoalPointX', 0), purePursuitTable.getNumber('GoalPointY', 0), '#00FF00')

    master.after(FRAME_TIME, draw)

master.after(FRAME_TIME, draw)

master.lift()
# master.call('wm', 'attributes', '.', '-topmost', '1')

mainloop()
