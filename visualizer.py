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
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 1000
AXIS_WIDTH = 2
AXIS_PADDING = 20
PATH_DATA = [
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
    [36.0, 60.0],
    [-20, 4]
]

# Smart Dashboard data for the path
PATH_DATA = []
x_coords = valuesTable.getNumberArray("PathXCoords", [])
y_coords = valuesTable.getNumberArray("PathYCoords", [])
for i in range(min(len(x_coords), len(y_coords))):
    PATH_DATA.append([x_coords[i], y_coords[i]])

BUFFER = 1.15
DEFAULT_X_SCALE = 3.0

x_coords = []
y_coords = []
for i in PATH_DATA:
    x_coords.append(i[0])
    y_coords.append(i[1])
smallest_x_val = min(x_coords)
largest_x_val = max(x_coords)
largest_y_val = max(y_coords)
# if smallest_x_val < 0:
#     X_SCALE_MIN = smallest_x_val * BUFFER
# else:
#     X_SCALE_MIN = -DEFAULT_X_SCALE
# if largest_x_val > 0:
#     X_SCALE_MAX = largest_x_val * BUFFER
# else:
#     X_SCALE_MAX = DEFAULT_X_SCALE
X_SCALE_MAX = 60
X_SCALE_MIN = -60
Y_SCALE_MAX = 120
Y_SCALE_MIN = -3
GRIDLINE_WIDTH = CANVAS_WIDTH / (X_SCALE_MAX - X_SCALE_MIN)
GRIDLINE_HEIGHT = CANVAS_HEIGHT / (Y_SCALE_MAX - Y_SCALE_MIN)
X_AXIS_POSITION = Y_SCALE_MAX * GRIDLINE_HEIGHT
Y_AXIS_POSITION = abs(X_SCALE_MIN) * GRIDLINE_WIDTH
POINT_RADIUS = 5
ROBOT_LINE_LENGTH = 100
robot_position_x = 0
robot_position_y = 0

# Connfigure window

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
    global robot_position_x
    global robot_position_y
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
    draw_robot(valuesTable.getNumber("PositionX", 0), valuesTable.getNumber("PositionY", 0), autoPopulateTable.getNumber("Gyro", 0))

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
