import numpy as np
import matplotlib.pyplot as plt
from cmath import sqrt
import time

start = time.time() #Samples clock (returns time since epoch) at this time
start_cpu = time.process_time() #Samples clock (system and CPU usage time) at this time

r = 1 #Radius
pi_real = 3.141592

grid = 1008 #grid dimension
step = 2/grid #dimension of each grid box

n = grid + 1 #grid + 1 is the number of points to build each side of the grid
x = np.arange(-1, 1+step, step)
y = x

count = dict(inside = 0, out = 0) #Dictionary to help count the points 
                                  #inside the circle and outside the circle
print("="*50, " Exercise 3.1 (Single Core execution) ","="*50)

for j in range(0, len(x)):
    for k in range(0, len(y)):
        pc = pow(x[j], 2) + pow(y[k], 2) #Circle parametrization
        if pc <= pow(r, 2): #Condition to be inside the circle
            count['inside'] += 1 #Increases the corresponding dictionary key for a point inside the circle
            #plt.scatter(x[j], y[k], c = 'orange') #Plot of the random points
        else:
            count['out'] += 1 #Increases the corresponding dictionary key for a point outside the circle
            #plt.scatter(x[j], y[k], c = 'blue') #Plot of the random points

print ("For {} points there are {} inside and {} outside.".format(pow(n, 2),count['inside'], count['out']))

z_c = 1 #Critical value
pi = 4*(count['inside'] / pow(n, 2)) #pi approximation formula
delta_r = 4*z_c*sqrt((count['inside'] / pow(n,2))*(1-(count['inside'] / pow(n,2)))/pow(n,2)) #Estimated error
delta_pi = abs(pi_real-pi) #Error
print("\nThe approximate value of pi is {:.6f}, the delta_r is {:.6f} and the delta_pi is {:.6f} for a critical value Z_c of {}.".format(pi, delta_r.real, delta_pi, z_c))

# circle1 = plt.Circle((0, 0), r, color='pink', fill=False) #matplotlib functionally to draw a circle with center
# #                                                        #at (0,0) and radius 1
# plt.gca().add_patch(circle1) #Drawing the circle (patch) in the plot at the current axis configuration
# #                              #gca() => Get Current Axis
# plt.grid()
# plt.show()

end = time.time() #Samples clock again
end_cpu = time.process_time() #same thing bit for system and CPU
et = end - start #Calculates the difference between time samples (epoch related)
et_cpu = end_cpu - start_cpu #Calculates the difference but for the time spent on system and CPU

print("\nThe execution time is {} seconds and the CPU execution time is {} seconds".format( et, et_cpu))
