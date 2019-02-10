from tkinter import *
from math import *
# import threading
# from networktables import NetworkTables

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

FRAME_TIME = 20
WIDTH = 800
HEIGHT = 800
AXIS_WIDTH = 2
AXIS_PADDING = 20
EXAMPLE_DATA = [
    [1, 2],
    [4, 5],
    [8, 2]
]
PATH_POINTS = []
# x_coords = valuesTable.getEntry("PathXCoords").getNumberArray([])
# y_coords = valuesTable.getEntry("PathYCoords").getNumberArray([])
# for i in range(min(len(x_coords), len(y_coords))):
#     PATH_POINTS.append([x_coords[i], y_coords[i]])
MAXX = 15
MAXY = 15
GRIDLINE_WIDTH = (WIDTH - AXIS_PADDING) / MAXX
GRIDLINE_HEIGHT = (HEIGHT - AXIS_PADDING) / MAXY
POINT_RADIUS = 5
ROBOT_LINE_LENGTH = 100

master = Tk()
master.title("Visualizer")
w = Canvas(master, width=WIDTH, height=HEIGHT)
w.pack(expand=YES, fill=BOTH)
w.config(background="#FFFFFF")

def draw_axes():
    w.create_line(AXIS_PADDING, 0, AXIS_PADDING, HEIGHT, width=AXIS_WIDTH)
    w.create_line(0, HEIGHT - AXIS_PADDING, WIDTH, HEIGHT - AXIS_PADDING, width=AXIS_WIDTH)

def draw_grid():
    offset = AXIS_PADDING + GRIDLINE_WIDTH
    for i in range(0, MAXX):
        w.create_line(offset, 0, offset, HEIGHT)
        offset += GRIDLINE_WIDTH
    offset = (HEIGHT - AXIS_PADDING) - GRIDLINE_HEIGHT
    for i in range(0, MAXY):
        w.create_line(0, offset, WIDTH, offset)
        offset -= GRIDLINE_HEIGHT
    
def plot_point(x, y):
    x_coord = AXIS_PADDING + x * GRIDLINE_WIDTH
    y_coord = HEIGHT - (AXIS_PADDING + y * GRIDLINE_HEIGHT)
    w.create_oval(x_coord + POINT_RADIUS, y_coord + POINT_RADIUS, x_coord - POINT_RADIUS, y_coord - POINT_RADIUS, fill="#e07fde")

def plot_data():
    for point in EXAMPLE_DATA:
        plot_point(point[0], point[1])

def draw_robot(robotx, roboty, robotzRotation):
    robotzRotation *= -1
    robotx = AXIS_PADDING + robotx * GRIDLINE_WIDTH
    roboty = HEIGHT - (AXIS_PADDING + roboty * GRIDLINE_HEIGHT)
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
    w.delete('all')
    draw_axes()
    draw_grid()
    plot_data()
    draw_robot(5, 5, -50)
    master.after(FRAME_TIME, draw)

master.after(FRAME_TIME, draw)

master.lift()
master.call('wm', 'attributes', '.', '-topmost', '1')

mainloop()
