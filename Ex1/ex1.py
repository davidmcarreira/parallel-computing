from dice import *
from random import randint
import matplotlib.pyplot as plt
import numpy as np
import time

start = time.time() #Samples clock (returns time since epoch) at this time
start_cpu = time.process_time() #Samples clock (system and CPU usage time) at this time

events = int(10e2) #number of events
sides = 6 #number of sides per dice
n_dice = 2 #number of dices

D = dice(sides, n_dice).myDice() #Nested dictionary composed of dices (last dict stores the sum)
for j in range(events):
    n = [] #List to store index respective to number on each dice
    for i in range(1, n_dice+1): #for cycle for each dice 
        k = randint(1, sides) #Random number
        n.append(k)
        D[i][k] += 1 #The index (k) related to each throw is increased for the dice (i)
    sum_throw = sum(n) #Sum of the last throw
    D[n_dice+1][sum_throw] += 1 #Sum dictionary "increases" the index respective to the sum of the last throw 


print("Final Result: ", D[n_dice+1])
plt.bar(range(len(D[n_dice+1])), D[n_dice+1].values(), tick_label = list(D[n_dice+1].keys())) #Plot of the frequencies bar
plt.yticks(np.arange(0, max(D[n_dice+1].values())+1, step=max(D[n_dice+1].values())/10)) #y-axis scaling to the max values of frequency

end = time.time() #Samples clock again
end_cpu = time.process_time() #Same thing but for system and CPU
et = end - start #Calculates the difference between time samples (epoch related)
et_cpu = end_cpu - start_cpu #Calculates the difference but for the time spent on system and CPU

print("For {} events the execution time is {} seconds and the CPU execution time is {} seconds".format(events, et, et_cpu))
plt.show()

"""

After 5 runs, the average time of execution for 10e6 events, 
is 25 seconds (for both the epoch related time and the CPU/system usage time).

"""