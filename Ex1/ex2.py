from ctypes.wintypes import SIZE
from dice import *
from random import randint
import matplotlib.pyplot as plt
import numpy as np
import time
from mpi4py import MPI

comm = MPI.COMM_WORLD #Communicator to handle point-to-point communication
rank = comm.Get_rank() #Hierarchy of processes
size = comm.Get_size() #Number of processes


# start = time.time() #Samples clock (returns time since epoch) at this time
# start_cpu = time.process_time() #Samples clock (system and CPU usage time) at this time

#comm.Barrier() #Process synchronization
start = MPI.Wtime()

events = int(1000004)//size #Number of events divided by the number of processes
sides = 6 #Number of sides per dice
n_dice = 2 #Number of dices

max_time = [] #Metadata list to store the time in each process

D = dice(sides, n_dice).myDice() #Nested dictionary composed of dices (last dict stores the sum)
for j in range(events): #for loop to handle all the dice throwings aka events
    n = [] #List to store index respective to number on each dice
    for i in range(1, n_dice+1): #for cycle for each dice
        k = randint(1, sides) #Random number
        n.append(k)
        D[i][k] += 1 #The index (k) related to each throw is increased for the dice (i)
    sum_throw = sum(n) #Sum of the last throw
    D[n_dice+1][sum_throw] += 1 #Sum dictionary "increases" the index respective to the sum of the last throw


#-------------------- Parallelization portion of the code --------------------#
if rank == 0:
    #print("Process", rank, "has the following results: ", D)
    for p in range (1, size):
        #print("The p value is: ", p)
        Dp = comm.recv(source = p) #Receives data from process p
        #print("Process", p, "has the following results: ", Dp)

        for n in range(dice().min, dice().max+1): #Range from minimum sum possible to the maximum sum possible depending on the number of dices used
            D[n_dice+1][n] += Dp[n_dice+1][n] #Adds the new data to the final sum dictionary 
                                                #of the previously initiated nested dictionary 
    
        process_time = comm.recv(source = p, tag = 1)
        max_time.append(process_time)

    print("Final Result: ", D[n_dice+1])
    #plt.bar(range(len(D[n_dice+1])), D[n_dice+1].values(), tick_label = list(D[n_dice+1].keys())) #Plot of the frequencies bar
    #plt.yticks(np.arange(0, max(D[n_dice+1].values())+1, step=max(D[n_dice+1].values())/10)) #y-axis scaling to the max values of frequency
    

    end_master = MPI.Wtime()
    et_master = end_master - start
    max_time.append(et_master)
    print("Process {} took {} seconds.".format(rank, et_master))
    
    print("For {} events the execution time is {} seconds.".format(events*size, max(i for i in max_time))) #The elapsed time is equal to the maximum time elapsed on a process

    #plt.show()
else:
    comm.send(D, dest = 0) #Sends data to rank 0 process

    end_slave = MPI.Wtime()
    et_slave = end_slave - start
    comm.send(et_slave, dest = 0, tag = 1)
    print("Process {} took {} seconds.".format(rank, et_slave))

    """
    
    After 5 runs, the average time of execution for 10e6 events and 4 paralell processes,
    is 1,43 seconds.

    It is a clear improvement over the single core performance script, has it reduces, on average,
    the time by 57%.
    
    """