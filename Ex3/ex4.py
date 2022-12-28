from mpi4py import MPI
from cmath import sqrt
import numpy as np
import sys

comm = MPI.COMM_WORLD #Communicator to handle point-to-point communication
start = MPI.Wtime() #MPI Wall time
rank = comm.Get_rank() #Hierarchy of processes
size = comm.Get_size() #Number of processes

grid = int(sys.argv[1]) #grid dimension
n = grid #grid + 1 is the number of points to build each side of the grid, but because of discretisation of real numbers in a grid
         #we must omit one of the extreme points in order to prevent overlaping of the border points in the grid between processes
gpp = grid/size #grid boxes per process
step = 1/grid #dimension of each grid box

r = 1 #Radius
pi_real = 3.141592

#Points placed in intermediate intervals (half step) for each grid square, this way there's no overlapping and the solution is symmetric
x = np.arange((step/2), 1+(step/2), step)
y = []
for j in np.arange(step/2+rank*gpp*step, (rank*gpp*step)+gpp*step, step):
    y.append(j)

count = dict(inside = 0, out = 0) #Dictionary to help count the points 
                                  #inside the circle and outside the circle

max_time = [] #Metadata list to store the time in each process

for j in range(0, len(x)):
    for k in range(0, len(y)):
        pc = pow(x[j], 2) + pow(y[k], 2) #Circle parametrization
        if pc <= pow(r, 2): #Condition to be inside the circle
            count['inside'] += 1 #Increases the corresponding dictionary key for a point inside the circle
        else:
            break

#-------------------- Parallelization portion of the code --------------------#
if rank == 0:
    for p in range(1, size): #for loop to call each process p
        count_proc = comm.recv(source = p, tag = 0) #Dictionary that counts the points inside and outside the circle

        count['inside'] += count_proc['inside'] #Adds the new values to the dictionary key that counts the points inside the circle
        count['out'] += count_proc['out'] #Adds the new values to the dictionary key that counts the points outside the circle

        process_time = comm.recv(source = p, tag = 1)
        max_time.append(process_time)
    print ("For {} points there are {} inside and {} outside.".format(pow(n, 2),count['inside'], count['out']))


    z_c = 1 #Critical value
    pi = 4*(count['inside'] / pow(n, 2)) #pi approximation formula
    delta_r = 4*z_c*sqrt((count['inside'] / pow(n,2))*(1-(count['inside'] / pow(n,2)))/pow(n,2)) #Estimated error
    delta_pi = abs(pi_real-pi) #Error

    print("\nThe approximate value of pi is {:.6f}, the delta_r is {:.6f} and the delta_pi is {:.6f} for a critical value Z_c of {}.".format(pi, delta_r.real, delta_pi, z_c))

    end_master = MPI.Wtime()
    et_master = end_master - start
    max_time.append(et_master)
    print("Process {} took {} seconds.".format(rank, et_master))
    print("The max time is {} seconds.".format(max(i for i in max_time))) #The elapsed time is equal to the maximum time elapsed on a process
else:
    #Communicators responsible for sending the generated/calculated data to the "master" process (rank 0)
    comm.send(count, dest = 0, tag = 0)

    end_slave = MPI.Wtime()
    et_slave = end_slave - start
    comm.send(et_slave, dest = 0, tag = 1)
    print("Process {} took {} seconds.".format(rank, et_slave))

comm.Barrier() #Guarantees that all the processes are synchronized at this step so the following print is last in order
if rank==0:print("="*50 + " Exercise 3.4 (Parallelized Execution) for a %dx%d grid "%(grid, grid ) + "="*50)

"""

- For 10^8 points there are there are 78539847 inside and 0 outside (obviously).

- The approximate value of pi is 3.141594 (same as the previous exercise) and the real value is 3.141592, the delta_r is 0.000164 and the delta_pi is 0.000002 
for a critical value Z_c of 1 (same as the previous exercise as well). 

- For 10^8 events the execution time is 58.824976959 seconds (basically the same as the previous one) but each thread has a different execution time:
    - Process 0 took 58.824976959 seconds.
    - Process 1 took 49.331580817 seconds.
    - Process 2 took 37.493568089 seconds.
    - Process 3 took 23.094166943 seconds.

=> As expected, due to the symmetry of the system and because only the points inside the circle count, the results are the same!

"""