from ctypes.wintypes import SIZE
from dice import *
from random import randint
import matplotlib.pyplot as plt
import numpy as np
from mpi4py import MPI
from math import sqrt

def simulation(f_events, f_sides, f_n_dice):
    f_X = dice(sides, n_dice).myDice() #Nested dictionary composed of dices (last dict stores the sum)
    for j in range(f_events): #for loop to handle all the dice throwings aka events
        n = [] #List to store index respective to number on each dice
        for i in range(1, f_n_dice+1): #for cycle for each dice
            k = randint(1, f_sides) #Random number
            n.append(k)
            f_X[i][k] += 1 #The index (k) related to each throw is increased for the dice (i)
        sum_throw = sum(n) #Sum of the last throw
        f_X[f_n_dice+1][sum_throw] += 1 #Sum dictionary "increases" the index respective to the sum of the last throw
    return f_X

npp = int(1024)//4 #Number of events divided by the number of processes
sides = 6 #Number of sides per dice
n_dice = 2 #Number of dices

comm = MPI.COMM_WORLD #Communicator to handle point-to-point communication
start = MPI.Wtime()
rank = comm.Get_rank() #Hierarchy of processes
size = comm.Get_size() #Number of processes

flag = 0
run = 1
#-------------------- Parallelization portion of the code --------------------#
if rank == 0:
    seq = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    AUX = dict.fromkeys(seq, 0)
    wtime = []

    for p in range(1, size):
        #print("Run order sent to process ", p)
        comm.send(npp, dest = p, tag=11)
    
    while True:

        D = simulation(npp, sides, n_dice)
        #print("Process", rank, "has the following results: ", D)
        #print(D)
        for p in range(1, size):
                Dp = comm.recv(source = p, tag = 0) #Receives data from process p
                #print("Process", p, "has the following results: ", Dp)
                #print(Dp)
                for n in range(dice().min, dice().max+1): #Range from minimum sum possible to the maximum sum possible depending on the number of dices used
                    AUX[n] += Dp[n_dice+1][n] #Adds the new data to the final sum dictionary 
                                                        #of the previously initiated nested dictionary
        
        for n in range(dice().min, dice().max+1): #Range from minimum sum possible to the maximum sum possible depending on the number of dices used
            AUX[n] += D[n_dice+1][n]

        summ = 0
        mean_dev = 0
        prob = [1/36, 2/36, 3/36, 4/36, 5/36, 6/36, 5/36, 4/36, 3/36, 2/36, 1/36]
        for i in range(dice().min, dice().max+1):
            #print(sum(AUX[j] for j in AUX))
            exp = (prob[i-2])*(sum(AUX[j] for j in AUX))
            x = (AUX[i]-exp)/exp
            #print("The intermediate summ is: ", pow(x, 2))
            summ = summ + pow(x, 2)

        mean_dev = (1/11)*sqrt(summ)

        print("="*20, "Run {} for {} throws".format(run, (size*npp)), "="*20)
        print("Final Result: ", AUX, sum(AUX[i] for i in AUX))
        print("The deviation for {} accumulated throws is {}.\n".format(sum(AUX[j] for j in AUX), mean_dev))
        
        if mean_dev < 0.001:
            for p in range(1, size):
                #print("Stop order sent to process ", p)
                comm.send(0, dest = p, tag=11)
                timep = comm.recv(source = p, tag = 3)
                wtime.append(timep)
            print("Condition met ------> Terminated (Process {})".format(rank))

            break
        
        else:
            run += 1
            npp = 2*npp
            for p in range(1, size):
                #print("Run order sent to process ", p)
                comm.send(npp, dest = p, tag=11)

    end_master = MPI.Wtime()
    et_master = end_master - start
    wtime.append(et_master)
    print("Process {} elapsed time ------> {} seconds.\n".format(rank, et_master))
    print("The elapsed time is {} seconds, corresponding to the max ET of all processes.".format(max(wtime)))
        
else:
    while flag==0:
        n = comm.recv(source = 0, tag=11)
        if n!=0:
            S = simulation(n, sides, n_dice)
            comm.send(S, dest = 0, tag=0) #Sends data to rank 0 process

        else:
            flag = 1
            print("Stop flag received -> Terminated (Process {})".format(rank))
            comm.send(None, dest = 0, tag = 0)
            
            end_slave = MPI.Wtime()
            et_slave = end_slave - start
            print("Process {} elapsed time ------> {} seconds.\n".format(rank, et_slave))
            comm.send(et_slave, dest = 0, tag = 3)
            break

comm.Barrier() #Guarantees that all the processes are synchronized at this step so the following print is last in order
if rank==0:print("="*50 + " Exercise 4.1 (Parallelized Execution) " + "="*50)

"""

After 5 runs, the average time of execution for 10e6 events and 4 paralell processes,
is 15 seconds for the epoch related time and 14 seconds for the CPU/system usage time.

It is a clear improvement over the single core performance script, has it reduces, on average,
the time by 60%.

"""