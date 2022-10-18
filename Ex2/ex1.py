from cmath import sqrt
import random
import time
import sys
from xml.sax import default_parser_list
import numpy as np
import matplotlib.pyplot as plt

start = time.time() #Samples clock (returns time since epoch) at this time
start_cpu = time.process_time() #Samples clock (system and CPU usage time) at this time

n = int(sys.argv[1]) #Number of points

pi_real = 3.141592
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
    y.append(y_temp) #Appends the float to the y list

    i += 1 #Increases the cycle index

for j in range(0, len(x)):
    pc = pow(x[j], 2) + pow(y[j], 2) #Circle parametrization
    if pc <= pow(r, 2): #Condition to be inside the circle
        count['inside'] += 1 #Increases the corresponding dictionary key for a point inside the circle
        #plt.scatter(x[j], y[j], c = 'orange') #Plot of the random points
    else:
        count['out'] += 1 #Increases the corresponding dictionary key for a point outside the circle
        #plt.scatter(x[j], y[j], c = 'blue')

print ("There are {} points inside and {} outside.".format(count['inside'], count['out']))

z_c = 1 #Critical value
pi = 4*(count['inside'] / n) #pi approximation formula
delta_r = 4*z_c*sqrt((count['inside'] / n)*(1-(count['inside'] / n))/n) #Estimated error
delta_pi = abs(pi_real-pi) #Error
print("\nThe approximate value of pi is {:.6f}, the delta_r is {:.6f} and the delta_pi is {:.6f} for a critical value Z_c of {}.".format(pi, delta_r, delta_pi, z_c))

#circle1 = plt.Circle((0, 0), r, color='pink', fill=False) #matplotlib functionally to draw a circle with center
                                                       #at (0,0) and radius 1
#plt.gca().add_patch(circle1) #Drawing the circle (patch) in the plot at the current axis configuration
                             #gca() => Get Current Axis

end = time.time() #Samples clock again
end_cpu = time.process_time() #same thing bit for system and CPU
et = end - start #Calculates the difference between time samples (epoch related)
et_cpu = end_cpu - start_cpu #Calculates the difference but for the time spent on system and CPU

print("\nFor {} events the execution time is {} seconds and the CPU execution time is {} seconds".format(n, et, et_cpu))

#plt.show() #Shows the plot after everything intended is included in the figure

"""
During experimentation I concluded that plotting the points takes up a lot of computing power (increasing the time exponentially), 
since that is just a visulization tool that has no impacts in the results, for this purpose, the corresponding lines related to that 
are commented. Therefore, without graphics, the results are as follows:

- For 10^8 points there are 78539247 points inside and 21460753 outside.

- The approximate value of pi is 3.141570 and the real value is 3.141592, the delta_r is 0.000164 and the delta_pi is 0.000022 
for a critical value Z_c of 1. 

- For 10^8 events the execution time is 175.12400078773499 seconds and the CPU execution time is 174.423741705 seconds
"""