import numpy as np
from mpi4py import MPI
import sys
from cmath import sqrt

def elim_gauss(vpp, prev_line, new_recvbuf):
    if rank == 0: # Rank 0 needs to be separated because the first line is special, since it's used for calculating the ratio variable
                  # and this is always the rank that receives the first information
        for j in range(1, vpp): #Lines
            if prev_line[m] == 0: #Handles the cases where a 0 is in the diagonal, so it will be used in the denominator of the ratio
                print("\nRank {}:There's a zero on the diagonal, therefore, the determinant is zero \nand the condition of linear independence for all equations is broken.".format(rank))
                sys.exit()

            else:
                ratio = new_recvbuf[j][m]/prev_line[m]
                
            for k in range(n+1): #Columns
                new_recvbuf[j][k] = new_recvbuf[j][k] - ratio * prev_line[k]
    else:
        for j in range(vpp): #Lines
            if prev_line[m] == 0: #Handles the cases where a 0 is in the diagonal, so it will be used in the denominator of the ratio
                print("\nRank {}:There's a zero on the diagonal, therefore, the determinant is zero \nand the condition of linear independence for all equations is broken.".format(rank))
                sys.exit()
            else:
                ratio = new_recvbuf[j][m]/prev_line[m]
                
            for k in range(n+1): #Columns
                new_recvbuf[j][k] = new_recvbuf[j][k] - ratio * prev_line[k]

    return new_recvbuf

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

np.set_printoptions(linewidth=200)

input = sys.argv[1]
if input != "True": #Processing mode
    input = int(sys.argv[1])
else: #Activates debug mode if sys.argv[1] == "True"
    input = bool(sys.argv[1])


if rank == 0:
    # Ignore the following 2 conditions (just for handling the input)
    if input == True: #Debug mode
        Ab = np.array([[-sqrt(2).real, 2, 0, 1], [1, -sqrt(2).real, 1, 1], [0, 2, -sqrt(2).real, 1]], dtype = 'float')
        n = len(Ab)
    else: #Ranksort mode
        n = input
        Ab = np.array(np.random.randint(10, 20, size = (n, n+1)), dtype='float')
    
    for p in range(size):
        comm.send(n, dest = p)

    unmod_Ab = np.copy(Ab)  # Although the first iteration is equal, A will be modified throughout the process, therefore, the matrix to be Scattered
                # has a different name, in order to preserve the original matrix so the verification of the solution is possible without too much hassle
                # Note: Initially I called the arrat unmod_Ab uppon declaration and the did Ab=unmod_Ab and Scattered Ab (thinking unmod_Ab would stay unmodified)
                # But we cannot do because we are creating a reference (any change to Ab also changes unmod_Ab). In order to unmod_Ab to stay immutable, we need to use np.copy() 

    # All the matrices are in the expanded form, this way is easier to handle the calculation and only one Scatter is needed.
    # When we need to separate A from b we just simply slice the array using the (:) notation:          
    print("\nStep 1 ===> Matrix A:\n{}".format(Ab[:, :n]))
    print("Step 1 ===> Matrix b:\n{}\n".format(Ab[:, n]))
else:
    Ab = None

n = comm.recv(source = 0)
m = 0
while m < n: # Cycle that performs the m step calculations
    if rank == 0: # Master rank that will distribute all the necessary parts over the processes
        if m!= 0:
            Ab[m-1:, :] = new_Ab
            print("\nStep {} ===> Matrix A:\n{}".format(m+1, Ab[:, :n]))
            print("\nStep {} ===> Matrix b:\n{}\n".format(m+1, Ab[:, n]))
            
            if m<n-1: 
                if Ab[m, m] < 0.000001 or Ab[m, m] == 0: # Condition to determine if partial pivoting is needed
                    print("====> Problematic value ({}) at ({},{})! \n====> Partial pivoting line {}".format(Ab[m, m], m, m, m+1))
                    Ab[[m, m+1], :] = Ab[[m+1, m], :] #The submatrix of rows [m, m+1] is pivoted with the submatrix [m+1, m]


        if m<n-1: # Determining the new line that needs to be preserved to calculate the ratio
            prev_line = Ab[m]

        recvbuf_supp = np.array_split(Ab[m:, :], size) # Support array that stores the array split in unequal (when needed) or equal parts 
        for i in range(len(recvbuf_supp)): # Using len(recvbuf_supp) (which is the same as the number of processes) for better comprehension
            if i == 0:
                count = recvbuf_supp[0].shape[0]*recvbuf_supp[0].shape[1] #Count is equal to the line of the array multiplied by the column
            else:
                count = np.hstack([count, recvbuf_supp[i].shape[0]*recvbuf_supp[i].shape[1]])
        displ = [sum(count[:p]) for p in range(size)] # It's the displacement array, i.e, stores the index where the block of data starts in each process
        displ = np.array(displ)

        for p in range(size):
            comm.send(recvbuf_supp[p].shape[0], dest = p, tag = 1) # Number of lines per process of new array (non divisible by # of processes)

        sendbuf = Ab[m:, :] # Data to be Scattered over the processes

    else:
        count = np.empty(size, dtype='int')
        prev_line = np.empty([n+1], dtype='float')
        displ = None
        sendbuf = None

    if m == n-1: break # Because the matrix A is delayed one index, there's an extra step m, but the process needs to be stoped at m == n-1

    vpp = comm.recv(source = 0, tag = 1) # Value that corresponds to the number of lines per process of new array (non divisible by # of processes)
    new_recvbuf = np.empty([vpp, n+1], dtype = 'float') # Buffer that receives the data is created depending on the number of the received elements (since the number of data might not be divisible by the # of processes)
    comm.Bcast(prev_line, root = 0) # Sending the new line to all the processes (since all of them need it to calcualte ratio)
    comm.Bcast(count, root = 0) # Updating the count value on all proceses
    comm.Scatterv([sendbuf, count, displ, MPI.DOUBLE], new_recvbuf, root = 0) # Scattering only the needed data


    #Gaus_Jordan Elimination Method
    new_recvbuf = elim_gauss(vpp, prev_line, new_recvbuf)

    #print("Step {} Rank {}: Results: \n{}".format(m, rank, new_recvbuf))
    new_Ab = np.empty([n-m, n+1], dtype = 'float') # The number of lines of the new_A always reduces by one (pivot line that's broadcasted)
    comm.Gatherv(new_recvbuf, [new_Ab, count, displ, MPI.DOUBLE], root = 0) # Gather the results 
    
    m += 1

# Backward Substitution
if rank == 0:
    #Because all the calculations were performed with the matrix in expanded mode, now it needs to be separated
    a = np.array(Ab[:, :n]) # The matrix A is all the rows and all the columns until n-1 (the slicing excludes the uppermost limit)
    b = np.array(Ab[:, n]) # The matrix b is all the rows but only the column n
    x = np.zeros_like(b) # Line array to be filled with the solutions
    x_str = ""
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - sum(a[i][j] * x[j] for j in range(i + 1, n))) / a[i][i]
        x_str = x_str + "\n====> x" + str(i+1) + ": " + str(x[i])
    print("The final solution is: " + x_str)

""""


Ignore the following section


"""
comm.Barrier()
if rank==0:
    print("\n"+"="*190)
    print("\nPrint the initial expanded form matrix Ab is: \n{}".format(unmod_Ab))
    original_b = unmod_Ab[:, n]
    test = np.matmul(unmod_Ab[:, :n], np.transpose(x))
    print("\nThe original b vector is {} and the verification vector is {}".format(original_b, test))
    verif = test - original_b
    if verif.any() == 0:
        print("====> Conclusion: The result is incorrect!")
    else:
        print("====> Conclusion: The result is correct!")
    print("\n" + "="*60 + " Exercise 7.2 (Gauss-Jordan Elimination Method with partial pivoting) " + "="*60)