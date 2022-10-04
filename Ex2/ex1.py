import random
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

start = time.time() #Samples clock (returns time since epoch) at this time
start_cpu = time.process_time() #Samples clock (system and CPU usage time) at this time

n = int(1600) #Number of points

x = [] #List with the x coordinates of the random points
y = [] #List with the y coordinates of the random points
r = 1 #Radius

count = dict(inside = 0, out = 0) #Dictionary to help count the points 
                                  #inside the circle and outside the circle

i = 0 #While cycle index
while i<n: #Cycle to fill 2 lists of the random numbers' coordinates
    x_temp = random.uniform(-1, 1) #Generates a random float between -1 and 1
    x.append(x_temp) #Appends the float to the x list

    y_temp = random.uniform(-1, 1)
    y.append(y_temp) #Appends the float to the x list

    i += 1 #Increases the cycle index

for j in range(0, len(x)):
    p = pow(x[j], 2) + pow(y[j], 2)
    if p < pow(r, 2):
        #print("The point is INSIDE the circle")
        count['inside'] += 1
        plt.scatter(x[j], y[j], c = 'orange') #Plot of the random points
    else:
        #print("The point is OUTSIDE the circle")
        count['out'] += 1
        plt.scatter(x[j], y[j], c = 'blue')

print ("There are {} points inside and {} outside.".format(count['inside'], count['out']))
circle1 = plt.Circle((0, 0), r, color='pink', fill=False) #matplotlib functionally to draw a circle with center
                                                       #at (0,0) and radius 1

pi = 4*(count['inside'] / n) #pi approximation formula

print("The approximate value of pi is {:.6f} ".format(pi))

plt.gca().add_patch(circle1) #Drawing the circle (patch) in the plot at the current axis configuration
                             #gca() => Get Current Axis





end = time.time() #Samples clock again
end_cpu = time.process_time() #same thing bit for system and CPU
et = end - start #Calculates the difference between time samples (epoch related)
et_cpu = end_cpu - start_cpu #Calculates the difference but for the time spent on system and CPU

print("For {} events the execution time is {} seconds and the CPU execution time is {} seconds".format(n, et, et_cpu))

plt.show() #Shows the plot after everything intended is included in the figure