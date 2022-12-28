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
rank = comm.Get_rank() #Hierarchy of processes
size = comm.Get_size() #Number of processes

#-------------------- Parallelization portion of the code --------------------#

seq = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
AUX = dict.fromkeys(seq, 0) #Auxiliary dictionary
mean_dev = 1
run = 1
while True:
    msg = comm.bcast(npp, root = 0)
    
    D = simulation(npp, sides, n_dice) #Simulation calculated for each process
        
    Dp = comm.gather(D, root = 0) #Simulation results gathered on root 0

    if rank==0:
        summ = 0
        prob = [1/36, 2/36, 3/36, 4/36, 5/36, 6/36, 5/36, 4/36, 3/36, 2/36, 1/36] #List of probabilities of each sum

        for p in range(0, size): 
                for n in range(dice().min, dice().max+1): #Range from minimum sum possible to the maximum sum possible depending on the number of dices used
                    AUX[n] += Dp[p][n_dice+1][n] #Adds the new data to the final sum dictionary 
                                                                #of the previously initiated nested dictionary

        print("="*20, "Run {} for {} throws".format(run, (size*npp)), "="*20)
        print("Final Result: ", AUX, sum(AUX[j] for j in AUX))

        #Mean deviation calculation
        for i in range(dice().min, dice().max+1):
            exp = (prob[i-2])*(sum(AUX[j] for j in AUX))
            x = (AUX[i]-exp)/exp
            summ = summ + pow(x, 2)

        mean_dev = (1/11)*sqrt(summ)
        print("The deviation for {} accumulated throws is {}.\n".format(sum(AUX[j] for j in AUX), mean_dev))

    new_mean_dev = comm.bcast(mean_dev, root = 0) #Updating the mean deaviation in each process

    if new_mean_dev < 0.001:
        break
        
    else:
        run += 1
        npp = 2*npp #Doubling the number of throws is the condition is not met
        #print("The new npp is: ", npp)

comm.Barrier() #Guarantees that all the processes are synchronized at this step so the following print is last in order
if rank==0:print("="*50 + " Exercise 5.1 (Parallelized Execution) " + "="*50)