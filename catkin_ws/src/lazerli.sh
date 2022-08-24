#!/bin/bash
gedit&
roslaunch labirent_ortam labirent_ortam.launch &
roslaunch turtlebot3_slam turtlebot3_slam.launch &
roslaunch turtlebot3_teleop turtlebot3_teleop_key.launch 


