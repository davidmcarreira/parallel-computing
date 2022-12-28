import random
from re import X
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpi4py import MPI
from cmath import sqrt


comm = MPI.COMM_WORLD #Communicator to handle point-to-point communication
start = MPI.Wtime() #MPI Wall time
rank = comm.Get_rank() #Hierarchy of processes
size = comm.Get_size() #Number of processes

n = int(sys.argv[1])  #Number of points divided by the number of processes
npp = n / size #Number of points per process

pi_real = 3.141592
x = [] #List with the x coordinates of the random points
y = [] #List with the y coordinates of the random points
r = 1 #Radius

max_time = [] #Metadata list to store the time in each process

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
        count_proc = comm.recv(source = p, tag = 3) #Dictionary that counts the points inside and outside the circle

        count['inside'] += count_proc['inside'] #Adds the new values to the dictionary key that counts the points inside the circle
        count['out'] += count_proc['out'] #Adds the new values to the dictionary key that counts the points outside the circle

        process_time = comm.recv(source = p, tag = 1)
        max_time.append(process_time)

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

    end_master = MPI.Wtime()
    et_master = end_master - start
    max_time.append(et_master)
    print("Process {} took {} seconds.".format(rank, et_master))

    print("\nFor {} events the execution time is {} seconds.".format(n, max(i for i in max_time)))

    #plt.show() #Shows the plot after everything intended is included in the figure
else:
    #Communicators responsible for sending the generated/calculated data to the "master" process (rank 0)
    comm.send(count, dest = 0, tag = 3)

    end_slave = MPI.Wtime()
    et_slave = end_slave - start
    comm.send(et_slave, dest = 0, tag = 1)
    print("Process {} took {} seconds.".format(rank, et_slave))


"""
During experimentation I concluded that plotting the points takes up a lot of computing power (increasing the time exponentially), 
since that is just a visulization tool that has no impacts in the results, for this purpose, the corresponding lines related to that 
are commented. Therefore, without graphics, the results are as follows:

-> Using 4 processes

- For 10^8 points there are 78541966 points inside and 21458034 outside.

- The approximate value of pi is 3.141679 and the real value is 3.141592, the delta_r is 0.000164 and the delta_pi is 0.000087 
for a critical value Z_c of 1. 

- For 10^8 events the execution time is 94.100734174 seconds. This means that there is a reduction of execution time of, approximately,
68 seconds, resulting in an improvement of ~42% when compared to single core performace!
"""