
import numpy as np
from mpi4py import MPI
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

n = 4 #Number of lines and/or columns
lpp = n // size #Columns per process

if rank == 0:
    A = np.array([[2, 2, 1, 1], [1, -3, 2, 3], [-1, 1, -1, -1], [1, -1, 1, 2]], dtype = 'float64')
    #A = np.array(np.linspace(1, n**2, num = 64, endpoint=True).reshape(n, n), dtype = 'float64')
    #A = np.array(np.random.randint(100, 200, size = (n, n)), dtype='float')
    #b = np.array([5, 2, -1, 2], dtype = 'int').reshape(1, 4)
    #Ab = np.array([[2, 2, 1, 1, 5], [1, -3, 2, 3, 2], [-1, 1, -1, -1, -1], [1, -1, 1, 2, 2]], dtype = 'float64')
    
    prev_line = A[0]
    new_A = np.empty([n, n], dtype = 'float64')

else:
    A = None
    Ab = None
    prev_line = np.empty([n], dtype='float64')
    new_A = None

recvbuf_A = np.empty([lpp, n], dtype = 'float64')
comm.Scatter(A, recvbuf_A, root = 0)


m = 0
while m < n-1:
    #print(m)
    if m == 0:
        comm.Bcast(prev_line, root = 0)
        print("Step 0: This is broadcasted ", prev_line)

    i = m
    if rank == 0:
        for j in range(i+1, lpp): #Lines
            if prev_line[i] == 0:
                ratio = recvbuf_A[j][i]/prev_line[i+1] #Ratio needs the line from the step m
            else:
                ratio = recvbuf_A[j][i]/prev_line[i]
            
            for k in range(n): #Columns
                    recvbuf_A[j][k] = recvbuf_A[j][k] - ratio * prev_line[k]
        #print("The line for step", m+1, prev_line)
        #print("\n", recvbuf_A, rank, i)

    else: #======> This is acting up, needs fixing but the parallelization is working properly
        print("Inside else: ", prev_line, m)
        for j in range((m//size), lpp): #Lines
            if prev_line[i] == 0:
                ratio = recvbuf_A[j][i]/prev_line[i+1] #Ratio needs the line from the step m
            else:
                ratio = recvbuf_A[j][i]/prev_line[i]

            for k in range(n): #Columns
                recvbuf_A[j][k] = recvbuf_A[j][k] - ratio * prev_line[k]
            #print("The ratio is", ratio, prev_line[i], rank)
        #print("The line for step", m+1, prev_line) 
        #print("\n", recvbuf_A, rank, i)

    comm.Gather(recvbuf_A, new_A, root=0)

    if rank == 0:
        print("="*50)
        print("Step {}: Matrix \n{}".format(m, new_A))
        if m < 3:
            prev_line = new_A[m+1]
        
    comm.Bcast(prev_line, root = 0)
    print("Step {}: This is broadcasted {}".format(m, prev_line))
    #print("Step {}: Line preserved {}\n".format(m, prev_line))
    
    m += 1
    