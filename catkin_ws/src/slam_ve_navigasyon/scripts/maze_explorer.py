#!/usr/bin/env python

import rospy, time
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
maxDistance = 0.0
def scan_callback(msg):
    global range_front
    global range_right
    global range_left
    global ranges
    global min_front,i_front, min_right,i_right, min_left ,i_left
    
    ranges = msg.ranges
    # get the range of a few points
    # in front of the robot (between 5 to -5 degrees)
    range_front[:5] = msg.ranges[5:0:-1]  
    range_front[5:] = msg.ranges[-1:-5:-1]
    # to the right (between 300 to 345 degrees)
    range_right = msg.ranges[300:345]
    # to the left (between 15 to 60 degrees)
    range_left = msg.ranges[60:15:-1]
    # get the minimum values of each range 
    # minimum value means the shortest obstacle from the robot
    min_range,i_range = min( (ranges[i_range],i_range) for i_range in range(len(ranges)) )
    min_front,i_front = min( (range_front[i_front],i_front) for i_front in range(len(range_front)) )
    min_right,i_right = min( (range_right[i_right],i_right) for i_right in range(len(range_right)) )
    min_left ,i_left  = min( (range_left [i_left ],i_left ) for i_left  in range(len(range_left )) )
    

# Initialize all variables
range_front = []
range_right = []
range_left  = []
min_front = 0
i_front = 0
min_right = 0
i_right = 0
min_left = 0
i_left = 0





# Create the node
cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1) # to move the robot
scan_sub = rospy.Subscriber('scan', LaserScan, scan_callback)   # to read the laser scanner
rospy.init_node('maze_explorer')



#============ FERHAT ================

RADIUS=3.24
def odometryCb(msg):
    global x2
    x2 = round(msg.pose.pose.position.x,2)
    global y2 
    y2 = round(msg.pose.pose.position.y,2)

    

def checkZone():
    x1 = -2
    y1 = -9.7
    #x2 = round(msg.pose.pose.position.x,2)
    #y2 = round(msg.pose.pose.position.y,2)
    distance = ((x1-x2)**2+(y1-y2)**2)**(1/2)
    global maxDistance
    if (distance>maxDistance):
        maxDistance=distance
    if (distance <= RADIUS and maxDistance>5):
        command.angular.z = 0.0    # if nothing near, go forward
        command.linear.x = 0.0
        cmd_vel_pub.publish(command)
        a=input("Robot baslangic konumuna dondu. Devam etmek icin tiklayiniz!..")

#rospy.init_node('oodometry', anonymous=True) #make node 
rospy.Subscriber('odom',Odometry,odometryCb)

#====================================
command = Twist()
command.linear.x = 0.0
command.angular.z = 0.0
        
rate = rospy.Rate(10)
time.sleep(1) # wait for node to initialize

near_wall = 0 # start with 0, when we get to a wall, change to 1

# Turn the robot right at the start
# to avoid the 'looping wall'
print("Turning...", x2, "  ", y2)
command.angular.z = -0.5
command.linear.x = 0.1
cmd_vel_pub.publish(command)
time.sleep(2)
       
while not rospy.is_shutdown():
    print("min front:", min_front)
    # The algorithm:
    # 1. Robot moves forward to be close to a wall
    # 2. Start following left wall.
    # 3. If too close to the left wall, reverse a bit to get away
    # 4. Otherwise, follow wall by zig-zagging along the wall
    # 5. If front is close to a wall, turn until clear
    while(near_wall == 0 and not rospy.is_shutdown()): #1
        print("Moving towards a wall.", x2, "  ", y2)
        checkZone()
        print("min front:", min_front)
        if(min_front > 0.7 and min_right > 0.7 and min_left > 0.7):    
            command.angular.z = -0.1    # if nothing near, go forward
            command.linear.x = 0.15
            print ("C", x2, "  ", y2)
        elif(min_left < 0.7):           # if wall on left, start tracking
            near_wall = 1       
            print ("A", x2, "  ", y2)            
        else:
            command.angular.z =-0.30  # if not on left, turn right 
            command.linear.x = 0.3

        cmd_vel_pub.publish(command)
        checkZone()
        
    else:   
        checkZone()
        # left wall detected
        if(min_front > 0.7): #2
            if(min_left < 0.7):    #3
                print("Range: {:.2f}m - Too close. Backing up.".format(min_left))
                print(x2, "  ", y2)
                command.angular.z = -0.3
                command.linear.x = 0.3
            elif(min_left > 0.7):  #4
                print("Range: {:.2f}m - Wall-following; turn left.".format(min_left))
                print(x2, "  ", y2)
                command.angular.z = 0.5
                command.linear.x = 0.3
            else:
                print("Range: {:.2f}m - Wall-following; turn right.".format(min_left))
                command.angular.z = -0.3
                command.linear.x = 0.3
            checkZone()    
        else:   #5
            checkZone()
            print("Front obstacle detected. Turning away.")
            print(x2, "  ", y2)
            command.angular.z = -2.0
            command.linear.x = 0.1
            cmd_vel_pub.publish(command)
            while(min_front < 0.3 and not rospy.is_shutdown()):      
                checkZone()
                pass
        # publish command 
        cmd_vel_pub.publish(command)
        print("min front:", min_front)
    # wait for the loop
    rate.sleep()
