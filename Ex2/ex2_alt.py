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

n = int(sys.argv[1]) #Number of points 
npp = n // (size - 1) #Floor division of the number of points by the number of processes
r = 1 #Radius
pi_real = 3.141592 #pi value

#-------------------- Parallelization portion of the code --------------------#
if rank == 0: #Master process
    x = [] #List with the x coordinates of the random points
    y = [] #List with the y coordinates of the random points
    count = dict(inside = 0, out = 0) #Dictionary to help count the points 
                                  #inside the circle and outside the circle
    #Cycle auxiliary variables
    process = 1
    recvd_data = 1
    n_points = 0

    while process < size: #Initializes all the slave processes, preparing the master to receive data back
        comm.send(x, dest = process, tag = 1)
        comm.send(y, dest = process, tag = 2)
        process += 1
       
    while recvd_data < size: #Cycle that receives the processed data and appends it to the coordinates arrays
        x2 = comm.recv(source = MPI.ANY_SOURCE, tag = 3)
        y2 = comm.recv(source = MPI.ANY_SOURCE, tag = 4)
        #print("Data received from process".format(MPI.ANY_SOURCE))
        for i in x2:
            x.append(i) #Appends newly received data to the x coordinates array
        for j in y2:
            y.append(j) #Appends newly received data to the y coordinates array

        recvd_data += 1


    for k in range(0, len(x)): #for loop to check if a point is inside the circle
        circ = pow(x[k], 2) + pow(y[k], 2)
        if circ < pow(r, 2):
            count['inside'] += 1 #Increases the corresponding dictionary key for a point inside the circle
        else:
            count['out'] += 1 #Increases the corresponding dictionary key for a point outside the circle


    z_c = 1 #Critical value
    pi = 4*(count['inside'] / n) #pi approximation formula
    delta_r = 4*z_c*sqrt((count['inside'] / n)*(1-(count['inside'] / n))/n) #Estimated error
    delta_pi = abs(pi_real-pi) #Error

    print ("There are {} points inside and {} outside.".format(count['inside'], count['out']))
    print("\nThe approximate value of pi is {:.6f}, the delta_r is {:.6f} and the delta_pi is {:.6f} for a critical value Z_c of {}.".format(pi, delta_r, delta_pi, z_c))

    end = time.time() #Samples clock again
    end_cpu = time.process_time() #Same thing but for system and CPU
    et = end - start #Calculates the difference between time samples (epoch related)
    et_cpu = end_cpu - start_cpu #Calculates the difference but for the time spent on system and CPU

    print("\nFor {} events the execution time is {} seconds and the CPU execution time is {} seconds.".format(n, et, et_cpu))

    #plt.show() #Shows the plot after everything intended is included in the figure

else: #Slave processes
    x_temp = comm.recv(source = 0, tag = 1)
    y_temp = comm.recv(source = 0, tag = 2)

    l = 0 #While cycle index
    while l<npp: #Cycle to fill 2 lists of the random numbers' coordinates
        x_rand = random.uniform(-1, 1) #Generates a random float between -1 and 1
        y_rand = random.uniform(-1, 1)
        x_temp.append(x_rand)
        y_temp.append(y_rand)
        l += 1
    
    comm.send(x_temp, dest = 0, tag = 3) #Sends data to rank 0 process
    comm.send(y_temp, dest = 0, tag = 4)
    
    #print("Process {} sent data.".format(rank))