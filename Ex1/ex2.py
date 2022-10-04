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

start = time.time() #Samples clock (returns time since epoch) at this time
start_cpu = time.process_time() #Samples clock (system and CPU usage time) at this time

events = int(16)//size #Number of events divided by the number of processes
sides = 6 #Number of sides per dice
n_dice = 2 #Number of dices

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
    print("Process", rank, "has the following results: ", D)
    for p in range (1, size):
        print("The p value is: ", p)
        Dp = comm.recv(source = p) #Receives data from process p
        print("Process", p, "has the following results: ", Dp)

        for n in range(dice().min, dice().max+1): #Range from minimum sum possible to the maximum sum possible depending on the number of dices used
            D[n_dice+1][n] += Dp[n_dice+1][n] #Adds the new data to the final sum dictionary 
                                                #of the previously initiated nested dictionary 
    

    print("Final Result: ", D[n_dice+1])
    plt.bar(range(len(D[n_dice+1])), D[n_dice+1].values(), tick_label = list(D[n_dice+1].keys())) #Plot of the frequencies bar
    plt.yticks(np.arange(0, max(D[n_dice+1].values())+1, step=max(D[n_dice+1].values())/10)) #y-axis scaling to the max values of frequency
    

    end = time.time() #Samples clock again
    end_cpu = time.process_time() #same thing bit for system and CPU
    et = end - start #Calculates the difference between time samples (epoch related)
    et_cpu = end_cpu - start_cpu #Calculates the difference but for the time spent on system and CPU
    print("For {} events the execution time is {} seconds and the CPU execution time is {} seconds".format(events*size, et, et_cpu))

    plt.show()
else:
    comm.send(D, dest = 0) #Sends data to rank 0 process

    """
    
    After 5 runs, the average time of execution for 10e6 events and 4 paralell processes,
    is 15 seconds for the epoch related time and 14 seconds for the CPU/system usage time.

    It is a clear improvement over the single core performance script, has it reduces, on average,
    the time by 60%.
    
    """