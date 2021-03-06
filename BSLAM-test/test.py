#!/usr/bin/python
#import the simulator and other stuff
from simulator import lidarSimulator
import simulator
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.components import Laser
from collections import namedtuple
import time
import math

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

Point = namedtuple('Point', 'x y')
Lineseg = namedtuple('Lineseg', 's e')

MAP_SIZE_PIXELS         = 1000
MAP_SIZE_METERS         = 20

room_pts = [Point(0, 0), Point(10, 0), Point(10, 2), Point(12, 2), Point(15,5),Point(15,10),Point(5,10), Point(5,12), Point(0,12)]
room = simulator.loop(room_pts)

obstacle = simulator.loop([Point(2,3), Point(3,3), Point(2.5,4)])

room = room + obstacle

lidarPoint = Point(4,4)
lidarAngle = 3

num_scans =  682
lidarRange = 10
noise = 0.0

#initialize lidar siulator
lidarSim = lidarSimulator(lidarPoint, lidarAngle, num_scans, lidarRange, noise, room)

#create laser model
laser = Laser(num_scans, 10, 360, 1000 * lidarRange, 0,0)

#initialize the slam
slam = RMHC_SLAM(laser, MAP_SIZE_PIXELS, MAP_SIZE_METERS, random_seed = 99348)

mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

positions = []
actual_pos = []
#simulate a scan of the lidar
for i in range(0,100):
    if(i > 10):
        lidarSim.translate(Point(0.01,0.1 * math.sin(i / 20)))
        lidarSim.rotate(0.01)
    actual_pos.append((lidarSim.position.x, lidarSim.position.y, lidarSim.angle))
    lidarSim.simLidar()
    scan = []
    scan = lidarSim.getScan()
    #print(scan)
    slam.update([1000 * s for s in scan], (10,0,0.1))
    
    x,y,theta = slam.getpos()
    
    if i %10 == 0:
        lidarSim.plotScan('scan' + str(i))
    slam.getmap(mapbytes)
    '''for i in range(0,MAP_SIZE_PIXELS):
        print([int(float(n)/26) for n in mapbytes[MAP_SIZE_PIXELS * i:MAP_SIZE_PIXELS * (i+1)]])'''
    print("X: " + str(x/1000) + ", Y: " + str(y/1000) + ", Angle: " + str(theta))
    positions.append((x,y,theta))
    #time.sleep(0.01)

fig = plt.figure(1)
plt.plot([p[0] for p in positions],[p[1] for p in positions], 'b.')
fig2 = plt.figure(2)
plt.plot([p[0] for p in actual_pos],[p[1] for p in actual_pos], 'b.')

import os
i = 0
while os.path.exists('{}{:d}.png'.format('path', i)):
    i += 1
fig.savefig('{}{:d}.png'.format('path', i))
fig2.savefig('{}{:d}.png'.format('realpath', i))