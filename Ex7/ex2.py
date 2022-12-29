import numpy as np
from mpi4py import MPI
import sys
from cmath import sqrt

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

np.set_printoptions(linewidth=200)
np.set_printoptions(suppress=True)

n = 3 #Number of lines and/or columns
lpp = n // size #Columns per process

if rank == 0:
    #A = np.array(np.random.randint(10, 20, size = (n, n)), dtype='float')
    #A = np.array([[2, 2, 1, 1, 5], [1, -3, 2, 3, 2], [-1, 1, -1, -1, -1], [1, -1, 1, 2, 2]], dtype = 'float')   
    A = np.array([[-sqrt(2).real, 2, 0, 1], [1, -sqrt(2).real, 1, 1], [0, 2, -sqrt(2).real, 1]], dtype = 'float64')
    print("\nStep 1 Matrix A:\n{}".format(A[:, :n]))
    print("Step 1 Matrix b:\n{}\n".format(A[:, n]))
else:
    A = None

m = 0
while m < n:
    if rank == 0:
        if m!= 0:
            A[m-1:, :] = new_A
            print("\nStep {} Matrix A:\n{}".format(m+1, A[:, :n]))
            print("Step {} Matrix b:\n{}\n".format(m+1, A[:, n]))

        if m<n-1:
            prev_line = A[m]

        recvbuf_supp = np.array_split(A[m:, :], size)
        for i in range(len(recvbuf_supp)): # Using len(recvbuf_supp) (which is the same as the number of processes) for better comprehension
            if i == 0:
                count = recvbuf_supp[0].shape[0]*recvbuf_supp[0].shape[1]
            else:
                count = np.hstack([count, recvbuf_supp[i].shape[0]*recvbuf_supp[i].shape[1]])
        displ = [sum(count[:p]) for p in range(size)] # It's the displacement array, i.e, stores the index where the block of data starts in each process
        displ = np.array(displ)
 

        for p in range(size):
            comm.send(recvbuf_supp[p].shape[0], dest = p, tag = 1) #Number of lines per process of new array (non divisible by # of processes)

        sendbuf = A[m:, :]

    else:
        count = np.empty(size, dtype='int')
        prev_line = np.empty([n+1], dtype='float')
        displ = None
        sendbuf = None

    if m == n-1: break #Because the matrix A is delayed one index, there's an extra step m, but the process needs to be stoped at m == n-1

    vpp = comm.recv(source = 0, tag = 1)
    new_recvbuf = np.empty([vpp, n+1], dtype = 'float')
    comm.Bcast(prev_line, root = 0)
    comm.Bcast(count, root = 0)
    comm.Scatterv([sendbuf, count, displ, MPI.DOUBLE], new_recvbuf, root = 0)

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

    #print("Step {} Rank {}: Results: \n{}".format(m, rank, new_recvbuf))
    new_A = np.empty([sum(count-1)//n, n+1], dtype = 'float')
    comm.Gatherv(new_recvbuf, [new_A, count, displ, MPI.DOUBLE], root = 0)
    #if rank == 0: print("Step {}: New A: \n{}\n".format(m, new_A))   
    
    m += 1

# if rank == 0:
#     # Backward Substitution
#     a = np.array(A[:, :n])
#     b = np.array(A[:, n])
#     # print("This is b", b, rank)
#     # print("This is a", a, rank)
#     x = np.zeros_like(b)
#     for i in range(n - 1, -1, -1):
#         x[i] = (b[i] - sum(a[i][j] * x[j] for j in range(i + 1, n))) / a[i][i]

#     print(x)

# recvbuf_x = np.empty([lpp, n+1], dtype = 'float')
# comm.Scatter(A, recvbuf_x, root = 0)

# #print(recvbuf_x, rank)

# # Backward Substitution
# a = np.array(recvbuf_x[:, :n])
# b = np.array(recvbuf_x[:, n])
# # print("This is b", b, rank)
# # print("This is a", a, rank)
# x = np.zeros_like(b)
# n = lpp
# for i in range(n - 1, -1, -1):
#     x[i] = (b[i] - sum(a[i][j] * x[j] for j in range(i + 1, 4))) / a[i][i]

# print(x, rank)