import random
from re import X
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpi4py import MPI

start = time.time() #Samples clock (returns time since epoch) at this time
start_cpu = time.process_time() #Samples clock (system and CPU usage time) at this time

comm = MPI.COMM_WORLD #Communicator to handle point-to-point communication
rank = comm.Get_rank() #Hierarchy of processes
size = comm.Get_size() #Number of processes

n = int(sys.argv[1])  #Number of points divided by the number of processes
print("n points: ", n)
npp = n // (size - 1)
r = 1 #Radius

#-------------------- Parallelization portion of the code --------------------#
if rank == 0:
    x = []
    y = []
    count = dict(inside = 0, out = 0) #Dictionary to help count the points 
                                  #inside the circle and outside the circle
    process = 1
    recvd_data = 1
    n_points = 0

    while process < size:
        comm.send(x, dest = process, tag = 1)
        comm.send(y, dest = process, tag = 2)
        print("Sending data to process {}".format(process))
        process += 1
        #print("Sending points {} to process {}".format(n_points, process))

       
    while recvd_data < size:
        x2 = comm.recv(source = MPI.ANY_SOURCE, tag = 3)
        y2 = comm.recv(source = MPI.ANY_SOURCE, tag = 4)
        #p = comm.recv(source=MPI.ANY_SOURCE, tag=11)
        print("Data received from process".format(MPI.ANY_SOURCE))
        for i in x2:
            x.append(i)

        for j in y2:
            y.append(j)

        recvd_data += 1


    for k in range(0, len(x)):
        circ = pow(x[k], 2) + pow(y[k], 2)
        if circ < pow(r, 2):
            #print("The point is INSIDE the circle")
            count['inside'] += 1
            #plt.scatter(x[k], y[k], c = 'orange') #Plot of the random points
        else:
            #print("The point is OUTSIDE the circle")
            count['out'] += 1
            #plt.scatter(x[k], y[k], c = 'blue')


    print(count)
    pi = 4*(count['inside'] / n) #pi approximation formula

    print("The approximate value of pi is {:.6f} ".format(pi))

    print ("There are {} points inside and {} outside.".format(count['inside'], count['out']))
    #circle1 = plt.Circle((0, 0), r, color='pink', fill=False) #matplotlib functionally to draw a circle with center
                                                       #at (0,0) and radius 1
    #plt.gca().add_patch(circle1) #Drawing the circle (patch) in the plot at the current axis configuration
                             #gca() => Get Current Axis

    end = time.time() #Samples clock again
    end_cpu = time.process_time() #same thing bit for system and CPU
    et = end - start #Calculates the difference between time samples (epoch related)
    et_cpu = end_cpu - start_cpu #Calculates the difference but for the time spent on system and CPU

    print("For {} events the execution time is {} seconds and the CPU execution time is {} seconds".format(n, et, et_cpu))

    #plt.show() #Shows the plot after everything intended is included in the figure

else:
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
    
    print("Process {} sent data.".format(rank))