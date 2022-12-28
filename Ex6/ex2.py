from mpi4py import MPI
import numpy as np
from cmath import sqrt
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

n = int(sys.argv[1])
lpp = int(n/sqrt(size).real)
np.set_printoptions(linewidth=200)

if rank == 0:
    firstIter = True
    #arr1 = np.linspace(1, n**2, n**2, dtype=int).reshape((n,n))
    #arr2 = np.transpose(np.linspace(10, 10*n**2, n**2, dtype=int).reshape((n, n))).copy()
    arr1 = np.random.randint(1000, size = (n, n), dtype = 'int') #Matrix of random integers
    arr2 = np.transpose(np.random.randint(1000, size = (n, n), dtype = 'int')).copy()
    sub_arr1 = np.split(arr1, int(n/lpp), axis = 0) #Spliting the matrix 1 in n/lpp lines per process
    sub_arr2 = np.split(arr2, int(n/lpp), axis = 0) #Spliting the matrix 2 inn/lpp columns per process

    print(sub_arr1)
    print(sub_arr2)

    mulbuf = np.empty([1, n**2], dtype = 'int')

    sendbuf = np.empty([lpp, 2*n], dtype='int')
    
    #First iteration of merging the 2 matrix together
    for i in sub_arr1:
        for j in sub_arr2:
            if firstIter:
                sendbuf = np.hstack((i, j))
                print("\nStacking : \n", sendbuf)
                firstIter = False
            else:
                stack = np.hstack((i, j))
                print("\nStacking :\n", stack)
                sendbuf = np.vstack((sendbuf, stack))
    print("\nThe sendbuf is: \n", sendbuf, sendbuf.shape)

else:
   sendbuf = None
   mulbuf = None

recvbuf = np.empty([lpp, 2*n], dtype='int') #Each process will receive an array with dimensions depending on the dimension of the sendbuf 
                                                     #(combination of possible multiplications after dividing the matrices), dimension of each matrix
                                                     #and sections of the matrix (n/m sections where n is the dimension of the matrix and m is the
                                                     # square root of the number of processes)
comm.Scatter(sendbuf, recvbuf,  root=0)
print("\n Rank {} received \n{} {}".format(rank, recvbuf, recvbuf.shape))

#=============================================== Matrix must be divided along the 0 axis and multiplied by the correspondent portion =========================================
mul_lpp = np.split(recvbuf, 2, axis = 1)
print("\n Rank {} will multiply the following portions \nA:\n{} \nB:\n{}".format(rank, mul_lpp[0], np.transpose(mul_lpp[1]), mul_lpp[0].shape))

mat_mul = np.matmul(mul_lpp[0], np.transpose(mul_lpp[1]))
print("\n Rank {} results: \n{} {}".format(rank, mat_mul, mat_mul.shape))

comm.Gather(mat_mul, mulbuf, root = 0) #Gathers the data in a serial array

if rank == 0:
    mulbuf = np.array_split(mulbuf[0], int((n**2)/lpp)) #The serial is split in a way that it can be divided through a series of array with dimension of the multiplication
                                                        #provided by each process
    print("\n"+"="*160)
    print("Matrix A is \n{} \n\nAnd matrix B is \n{}".format(arr1, np.transpose(arr2)))
    print("\n"+"="*160)
    #print("\nThe multiplication serial results is: \n", mulbuf, len(mulbuf))

    j = 0
    k = 0
    process = 0 #The proccess number will dictate the intervals of data in the results serial array
    while k < len(mulbuf)-lpp:
        layer = np.empty([lpp, lpp], dtype = 'int')
        if k<=n-lpp:
            while k<=n-lpp: #Creation of the first chunks
                chunk = np.asarray(mulbuf[k:k+lpp])
                if k == 0:
                    layer = chunk
                    print("Layer: \n", k, layer, layer.shape)
                else:
                    layer = np.hstack([layer, chunk])
                    print("Layer: \n", k, layer, layer.shape)
                k += lpp
                process += 1 #One chunk per process

            rebuilt_C = layer #First layer of the final matrix is created

        else:
            while layer.shape[1] < n:
                chunk = np.asarray(mulbuf[k:k+lpp])
                if (k%n) == 0:
                    layer = chunk
                    print("Starting chunk: \n", k, layer, layer.shape)
                    print("\n")

                else:
                    #chunk = np.asarray(mulbuf[k:k+lpp])
                    layer = np.hstack([layer, chunk])
                    print("Layer: \n", k, layer, layer.shape)

                k += lpp
            rebuilt_C = np.vstack([rebuilt_C, layer])
            process += 1
            
            
    print("\n"+"="*160)
    print(f"The final results is: \n", rebuilt_C, rebuilt_C.shape)


""""


Ignore the following section


"""
comm.Barrier()
if rank==0:
    print("\n"+"="*160)
    if n<1024:
        test = np.matmul(arr1, np.transpose(arr2))
        verif = rebuilt_C - test
        print("\nDebug result - Single core calculation for small NxN dimensions (<1024): \n", test, test.shape)
        
        if verif.any() != 0:
            print("\n====> The result and debug matrix are not the same, therefore, the multiplication is incorrect!")
        else:
            print("\n====> The result and debug matrix are the same, therefore, the multiplication is correct!")

    print("\n" + "="*60 + " Exercise 6.2 (Parallelized Execution) " + "="*61)