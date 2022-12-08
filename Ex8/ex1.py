from mpi4py import MPI
import numpy as np
from collections import Counter
from sys import argv

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

np.set_printoptions(linewidth=200)

input = argv[1]
if input != "True":
    input = int(argv[1])
else:
    input = bool(argv[1])

if rank == 0:
    if input == True: #
        unsorted_arr = np.asarray(np.hstack([np.arange(1, 5, 1), np.arange(4, 16, 1), np.arange(4, 24, 1)])/10, dtype='float') # For debug purposes (duplicates and other possible problems)
    else:
        n = input
        unsorted_arr = np.random.rand(n) # Generates a random number array (unsorted)

    unsorted_arr = np.asarray(list(set(unsorted_arr)), dtype='float')
    print("Unsorted array without duplicates: ", unsorted_arr, unsorted_arr.shape)

    n_values = len(unsorted_arr) #Size of the array after the duplicates are removed (used to initiate the buffers and loops)

    # All the data should be treated before any parallelization, therefore, we must remove the duplicates 
    # in the generated array. But as a consequence the removed duplicates can lead to an array that is not 
    # divisible by the number of processes and some data manipulation is needed:

    recvbuf_supp = np.array_split(unsorted_arr, size) # Ignore this (Array to aid in finding the recv buffer sizes)
    #print(recvbuf_supp)
    # recvbuf_size Array that has the size of each buffer that will receive Scattered data
    for i in range(len(recvbuf_supp)): # Using len(recvbuf_supp) (which is the same as the number of processes) for better comprhension
        if i == 0:
            recvbuf_size = len(recvbuf_supp[0])
        else:
            recvbuf_size = np.hstack([recvbuf_size, len(recvbuf_supp[i])])

    displ = [sum(recvbuf_size[:p]) for p in range(size)] # It's the displacement array, i.e, stores the index where the block of data starts in each process
    displ = np.array(displ)

    for p in range(0, size): # Sending the size of each receiving buffer to all the processes
        comm.send(recvbuf_size[p], dest = p, tag = 1)
        comm.send(n_values, dest = p, tag = 2)
    
    r = np.empty(n_values, dtype='int') # Buffer array to receive the Scattered ranks for sorting
    
else:
    n_values = comm.recv(source=0, tag = 2)
    unsorted_arr = np.empty(n_values, dtype='float') # Buffer array to receive the Broadcasted data
    recvbuf_size = np.empty(4, dtype='int') # Array that has the size of each buffer that will receive Scattered data

    # For Gather and Scatter methods, only the master rank (0) is relevant, but the passed variables still need to be declared
    r = None # If rank != 0 nothing is Gathered
    displ = None # If rank != 0 nothing is Scattered
    

comm.Bcast(unsorted_arr, root = 0) # The unsorted array is Broadcasted to all processes 
#if rank == 0: print("The broadcasted unsorted data is: \n{} {}".format(unsorted_arr, unsorted_arr.shape))

vpp = comm.recv(source=0, tag = 1)
print("The array at rank {} will have size {}".format(rank, vpp))
recvbuf = np.empty(vpp, dtype = 'float') # Buffer to receive all the values Scattered from the master to each process
comm.Scatterv([unsorted_arr, recvbuf_size, displ, MPI.DOUBLE], recvbuf, root = 0) # Using Scatterv because the recvbuf arrays will have different sizes
                                                                                  # since the removal of duplicates can incur in unsorted arrays with
                                                                                  # size non divisible by the number of processes

print("\n Rank {} received \n{}".format(rank, recvbuf))

r_chunk = np.empty(vpp, dtype='int') # Generates empty array to store the rank of each value
for i in range(vpp):
    idx = 0
    for j in range(n_values):
        if recvbuf[i] > unsorted_arr[j]: # Compares the value in postion i with all the j-th position values
            idx += 1  # If the value is bigger, an index is increased each time the condition is met

    r_chunk[i] = idx  # And the index is stored in the rank array


comm.Gatherv(r_chunk, [r, recvbuf_size, displ, MPI.DOUBLE], root = 0)
if rank == 0:
    #print(r, r.shape)
    sorted_arr = np.empty(n_values, dtype='float') # Generates empty array to store the sorted values
    for i in range (n_values):
        sorted_arr[r[i]] = unsorted_arr[i] # The sorted value index in the sorted array is extracted from the rank array and associated to the corresponding indexed value in the unsorted array

    print("\nThe original array is: \n{} {}\n".format(unsorted_arr, unsorted_arr.shape))
    print(r, r.shape)
    print("The sorted array without duplicates is: \n{} {}".format(sorted_arr, sorted_arr.shape))


""""


Ignore the following section


"""
comm.Barrier()
if rank==0: print("\n" + "="*60 + " Exercise 8 (Ranksort Algorithm) " + "="*61)