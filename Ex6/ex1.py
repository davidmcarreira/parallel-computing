import numpy as np
from mpi4py import MPI
import sys

n = int(sys.argv[1])
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

lpp = int(n/size) #Number of lines per process

if rank == 0:
    #Data to be broadcasted and scattered, hence only being created on rank 0

    #sendbuf_A = np.linspace(1, n**2, n**2, dtype=int).reshape((n,n))
    #mat_B = np.linspace(10, 10*n**2, n**2, dtype=int).reshape((n, n)) 

    sendbuf_A = np.random.randint(1000, size = (n, n), dtype = 'int') #Matrix of random integers
    mat_B = np.random.randint(1000, size = (n, n), dtype = 'int')
    

    recvbuf_C = np.empty([n, n], dtype = 'int') #Only rank 0 needs a buffer because it's a comm.Gather()

else:
    sendbuf_A = None #Ranks other than 0 scatter nothing, so no buffer is needed (but still needs to be declared)
    mat_B = np.empty([n, n], dtype = 'int') #Allocates memory to receive matrix B

    recvbuf_C = None #Ranks other than 0 gather nothing, so no buffer is needed (but still needs to be declared)

#The Scatter method is smart, so it divids the available data by all the processes, therefore, 
#the recvbuf needs the appropriate dimensions and data type
recvbuf_A = np.empty([lpp, n], dtype = 'int') #Allocates memory on all processes to receive their corresponding portion of matrix A
comm.Scatter(sendbuf_A, recvbuf_A, root = 0) #from sendbuf to recvbuf

comm.Bcast(mat_B, root = 0) #The matrix B is fully broadcasted for all the processes

print("\nThis is the portion of matrix A for rank {}: \n{}".format(rank, recvbuf_A))
#print("\n{} This is mat B: \n{}".format(rank, mat_B))

C = np.matmul(recvbuf_A, mat_B) #Matrix multiplication
print("\nThis is the portion of matrix C sent by rank {}: \n{}".format(rank, C))

comm.Gather(C, recvbuf_C,  root = 0) #The results from each process is gathered on the master 
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
    print("\n"+"="*160)
    if n<1024:
        test = np.matmul(sendbuf_A, mat_B)
        verif = recvbuf_C - test
        print("\nDebug result - Single core calculation for small NxN dimensions (<1024): \n", test, test.shape)
        
        if verif.any() != 0:
            print("\n====> The result and debug matrix are not the same, therefore, the multiplication is incorrect!")
        else:
            print("\n====> The result and debug matrix are the same, therefore, the multiplication is correct!")

    print("\n" + "="*60 + " Exercise 6.1 (Parallelized Execution) " + "="*61)