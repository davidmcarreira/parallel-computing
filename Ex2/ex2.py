import random
from re import X
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpi4py import MPI
from cmath import sqrt

start = time.time() #Samples clock (returns time since epoch) at this time
start_cpu = time.process_time() #Samples clock (system and CPU usage time) at this time

comm = MPI.COMM_WORLD #Communicator to handle point-to-point communication
rank = comm.Get_rank() #Hierarchy of processes
size = comm.Get_size() #Number of processes

n = int(sys.argv[1])  #Number of points divided by the number of processes
npp = n / size #Number of points per process

pi_real = 3.141592
x = [] #List with the x coordinates of the random points
y = [] #List with the y coordinates of the random points
r = 1 #Radius

count = dict(inside = 0, out = 0) #Dictionary to help count the points 
                                  #inside the circle and outside the circle

i = 0 #While cycle index
while i<npp: #Cycle to fill 2 lists of the random numbers' coordinates
    x_temp = random.uniform(-1, 1) #Generates a random float between -1 and 1
    x.append(x_temp) #Appends the float to the x list

    y_temp = random.uniform(-1, 1)
    y.append(y_temp) #Appends the float to the x list

    i += 1 #Increases the cycle index

for j in range(0, len(x)): #for loop to check if a point is inside the circle
    pc = pow(x[j], 2) + pow(y[j], 2) #Circle parametrization
    if pc <= pow(r, 2): #Condition to be inside the circle
        count['inside'] += 1 #Increases the corresponding dictionary key for a point inside the circle
        #plt.scatter(x[j], y[j], c = 'orange') #Plot of the random points
    else:
        count['out'] += 1 #Increases the corresponding dictionary key for a point outside the circle
        #plt.scatter(x[j], y[j], c = 'blue')


#-------------------- Parallelization portion of the code --------------------#
if rank == 0:
    for p in range(1, size): #for loop to call each process p
        x_proc = comm.recv(source = p, tag = 1) #Points x coordinates
        y_proc = comm.recv(source = p, tag = 2) #Points y coordinates
        count_proc = comm.recv(source = p, tag = 3) #Dictionary that counts the points inside and outside the circle

        count['inside'] += count_proc['inside'] #Adds the new values to the dictionary key that counts the points inside the circle
        count['out'] += count_proc['out'] #Adds the new values to the dictionary key that counts the points outside the circle

    z_c = 1 #Critical value
    pi = 4*(count['inside'] / n) #pi approximation formula
    delta_r = 4*z_c*sqrt((count['inside'] / n)*(1-(count['inside'] / n))/n) #Estimated error
    delta_pi = abs(pi_real-pi) #Error

    print ("There are {} points inside and {} outside.".format(count['inside'], count['out']))
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
else:
    #Communicators responsible for sending the generated/calculated data to the "master" process (rank 0)
    comm.send(x, dest = 0, tag = 1)
    comm.send(y, dest = 0, tag = 2)
    comm.send(count, dest = 0, tag = 3)


"""
During experimentation I concluded that plotting the points takes up a lot of computing power (increasing the time exponentially), 
since that is just a visulization tool that has no impacts in the results, for this purpose, the corresponding lines related to that 
are commented. Therefore, without graphics, the results are as follows:

-> Using 4 processes

- For 10^8 points there are 78540345 points inside and 21459655 outside.

- The approximate value of pi is 3.141503 and the real value is 3.141592, the delta_r is 0.000164 and the delta_pi is 0.000089 
for a critical value Z_c of 1. 

- For 10^8 events the execution time is 106.49144983291626 seconds and the CPU execution time is 103.981949305 seconds. This means that
there is a reduction of exectuion time of,approximately, 69 seconds, resulting in an improvemnt of 60.8% when compared to single core performace!

Note: This is basically the same percentage as the "Dice Rolling" task.
"""