import numpy as np
from mpi4py import MPI
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

np.set_printoptions(linewidth=200)
np.set_printoptions(suppress=True)

n = 4 #Number of lines and/or columns
lpp = n // size #Columns per process

if rank == 0:
    #A = np.array(np.random.randint(10, 20, size = (n, n)), dtype='float')
    A = np.array([[2, 2, 1, 1, 5], [1, -3, 2, 3, 2], [-1, 1, -1, -1, -1], [1, -1, 1, 2, 2]], dtype = 'float')
    
    prev_line = A[0]

    new_A = np.empty([n, n+1], dtype='float')

    print("Starting matrix: \n", A)
else:
    A = None
    new_A = None
    prev_line = np.empty([n+1], dtype='float')

recvbuf = np.empty([lpp, n+1], dtype = 'float')
comm.Scatter(A, recvbuf, root = 0)

#Upper Triangular Matrix
m = 0
while m < n-1:

    if m == 0:
        comm.Bcast(prev_line, root = 0)

        if rank == 0:
            for j in range(m+1, lpp): #Lines
                if prev_line[m] == 0:
                    ratio = recvbuf[j][m]/prev_line[m+1] #Ratio needs the line from the step m

                else:
                    ratio = recvbuf[j][m]/prev_line[m]
                
                for k in range(n+1): #Columns
                    recvbuf[j][k] = recvbuf[j][k] - ratio * prev_line[k]
        else:
            for j in range(lpp): #Lines
                ratio = recvbuf[j][m]/prev_line[m]
                
                for k in range(n+1): #Columns
                    recvbuf[j][k] = recvbuf[j][k] - ratio * prev_line[k]   

        comm.Gather(recvbuf, new_A, root = 0)
        if rank == 0: print("Step 0: New A:\n", new_A)

    else:
        #print("Step {} Rank {}: prev_line: \n{}".format(m, rank, prev_line))

        if rank == 0:
            for j in range(1, vpp): #Lines
                if prev_line[m] == 0:
                    ratio = new_recvbuf[j][m]/prev_line[m+1] #Ratio needs the line from the step m
                else:
                    ratio = new_recvbuf[j][m]/prev_line[m]
                
                for k in range(n+1): #Columns
                    new_recvbuf[j][k] = new_recvbuf[j][k] - ratio * prev_line[k]
        else:

            for j in range(vpp): #Lines
                ratio = new_recvbuf[j][m]/prev_line[m]
                
                for k in range(n+1): #Columns
                    new_recvbuf[j][k] = new_recvbuf[j][k] - ratio * prev_line[k]

        print("Step {} Rank {}: Results: \n{}".format(m, rank, new_recvbuf))
        new_A = np.empty([sum(count)//n, n+1], dtype = 'float')
        comm.Gatherv(new_recvbuf, [new_A, count, displ, MPI.DOUBLE], root = 0)
        if rank == 0: print("Step {}: New A: \n{}\n".format(m, new_A))   

        
    if rank == 0:
        if m == 0:
            A = new_A
        elif m!= 0 and m<n:
            A[m:, :] = new_A
            print("Complete A:\n", A[:, :n], m)
            print("Matrix b:\n",A[:, n])

        if m<n-1:
            prev_line = A[m+1]

        recvbuf_supp = np.array_split(A[m+1:, :], size)
        for i in range(len(recvbuf_supp)): # Using len(recvbuf_supp) (which is the same as the number of processes) for better comprehension
            if i == 0:
                count = recvbuf_supp[0].shape[0]*recvbuf_supp[0].shape[1]
            else:
                count = np.hstack([count, recvbuf_supp[i].shape[0]*recvbuf_supp[i].shape[1]])
        displ = [sum(count[:p]) for p in range(size)] # It's the displacement array, i.e, stores the index where the block of data starts in each process
        displ = np.array(displ)
 

        for p in range(size):
            comm.send(recvbuf_supp[p].shape[0], dest = p, tag = 1) #Number of lines per process of new array (non divisible by # of processes)

        sendbuf = A[m+1:, :]
    else:
        count = np.empty(size, dtype='int')
        displ = None
        sendbuf = None
    
    vpp = comm.recv(source = 0, tag = 1)
    new_recvbuf = np.empty([vpp, n+1], dtype = 'float')

    comm.Bcast(prev_line, root = 0)
    comm.Bcast(count, root = 0)
    comm.Scatterv([sendbuf, count, displ, MPI.DOUBLE], new_recvbuf, root = 0)

    #print("\nStep {}: Rank {} received \n{}\n".format(m, rank, new_recvbuf))
    m += 1

if rank == 0:
    #Backward Substitution
    x = [0] * n
    for i in range(n-1, -1, -1):
        x[i] = (A[i][n] - sum(A[i][j] * x[j] for j in range(i + 1, n))) / A[i][i]

    print(x)