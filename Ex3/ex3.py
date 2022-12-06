from mpi4py import MPI
from cmath import sqrt
import numpy as np

#start = time.time() #Samples clock (returns time since epoch) at this time
#start_cpu = time.process_time() #Samples clock (system and CPU usage time) at this time

comm = MPI.COMM_WORLD #Communicator to handle point-to-point communication
start = MPI.Wtime()
rank = comm.Get_rank() #Hierarchy of processes
size = comm.Get_size() #Number of processes

grid = 108 #grid dimension
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

total_time = 0

for j in range(0, len(x)):
    for k in range(0, len(y)):
        pc = pow(x[j], 2) + pow(y[k], 2) #Circle parametrization
        if pc <= pow(r, 2): #Condition to be inside the circle
            count['inside'] += 1 #Increases the corresponding dictionary key for a point inside the circle
        else:
            count['out'] += 1 #Increases the corresponding dictionary key for a point outside the circle

#-------------------- Parallelization portion of the code --------------------#
if rank == 0:
    for p in range(1, size): #for loop to call each process p
        count_proc = comm.recv(source = p, tag = 0) #Dictionary that counts the points inside and outside the circle

        count['inside'] += count_proc['inside'] #Adds the new values to the dictionary key that counts the points inside the circle
        count['out'] += count_proc['out'] #Adds the new values to the dictionary key that counts the points outside the circle

        process_time = comm.recv(source = p, tag = 1)
        total_time += process_time #THIS IS WRONG
    print ("For {} points there are {} inside and {} outside.".format(pow(n, 2),count['inside'], count['out']))

    z_c = 1 #Critical value
    pi = 4*(count['inside'] / pow(n, 2)) #pi approximation formula
    delta_r = 4*z_c*sqrt((count['inside']/pow(n,2)) * (1-(count['inside']/pow(n,2))) / pow(n,2)) #Estimated error
    delta_pi = abs(pi_real-pi) #Error

    print("\nThe approximate value of pi is {:.6f}, the delta_r is {:.6f} and the delta_pi is {:.6f} for a critical value Z_c of {}.".format(pi, delta_r.real, delta_pi, z_c))

    # end = time.time() #Samples clock again
    # end_cpu = time.process_time() #same thing bit for system and CPU
    # et = end - start #Calculates the difference between time samples (epoch related)
    # et_cpu = end_cpu - start_cpu #Calculates the difference but for the time spent on system and CPU
    # print("\nFor {} points the execution time is {} seconds and the CPU execution time is {} seconds".format(pow(n, 2), et, et_cpu))
    
    end_master = MPI.Wtime()
    et_master = end_master - start
    print("Process {} took {} seconds.".format(rank, et_master))
    print("The total time is {} seconds.".format(total_time))

else:
    #Communicators responsible for sending the generated/calculated data to the "master" process (rank 0)
    comm.send(count, dest = 0, tag = 0)

    end_slave = MPI.Wtime()
    et_slave = end_slave - start
    comm.send(et_slave, dest = 0, tag = 1)
    print("Process {} took {} seconds.".format(rank, et_slave))

comm.Barrier() #Guarantees that all the processes are synchronized at this step so the following print is last in order
if rank==0:print("="*50 + " Exercise 3.3 (Parallelized Execution) for a %dx%d grid "%(grid, grid ) + "="*50)