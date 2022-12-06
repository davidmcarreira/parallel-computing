import numpy as np
from mpi4py import MPI

n = 8
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

lpp = int(n/size)

if rank == 0:
    sendbuf_A = np.linspace(1, n**2, n**2, dtype=int).reshape((n,n)) #Only rank 0 needs a buffer because it's a comm.Scatter()
    mat_B = np.linspace(10, 10*n**2, n**2, dtype=int).reshape((n, n)) #Data to be broadcasted, hence only being created on rank 0

    recvbuf_C = np.empty([n, n]) #Only rank 0 needs a buffer because it's a comm.Gather()

else:
    sendbuf_A = None #Ranks other than 0 scatter nothing, so no buffer is needed
    mat_B = np.empty([n, n]) #Allocates memory to receive matrix B

    recvbuf_C = None #Ranks other than 0 gather nothing, so no buffer is needed

#The Scatter method is smart, so it divids the available data by all the processes, therefore, 
#the recvbuf needs the appropriate dimensions 
recvbuf_A = np.empty([lpp, n]) #Allocates memory on all processes to receive their corresponding portion of matrix A
comm.Scatter(sendbuf_A, recvbuf_A, root = 0) #from sendbuf to recvbuf

comm.Bcast(mat_B, root = 0) #The matrix B is fully broadcasted for all the processes

print("\nThis is the portion of matrix A for rank {}: \n{}".format(rank, recvbuf_A))
#print("\n{} This is mat B: \n{}".format(rank, mat_B))

C = np.matmul(recvbuf_A, mat_B)
print("\nThis is the portion of matrix C sent by rank {}: \n{}".format(rank, C))

comm.Gather(C, recvbuf_C,  root = 0)
if rank ==0:
    print("\n"+"="*80)
    print("Matrix A is \n{} \n\nAnd matrix B is \n{}".format(sendbuf_A, mat_B))
    print("\n"+"="*80)
    print("The final results is: \n", recvbuf_C)

""""


Ignore the following section


"""
comm.Barrier()
if rank==0:
    test = np.matmul(np.linspace(1, n**2, n**2).reshape((n,n)), mat_B)
    print("\nDebug result: \n", test)
    print("\n" + "="*50 + " Exercise 6.1 (Parallelized Execution) " + "="*50)
