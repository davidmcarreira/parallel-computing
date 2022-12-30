"""

Tenho de paralelizar a Backward Substitution?

Preciso de verificar se as equações são linearmente independentes a cada passo?

"""

import numpy as np
from mpi4py import MPI
from sys import argv
from cmath import sqrt

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

np.set_printoptions(linewidth=200)

input = argv[1]
if input != "True": #Processing mode
    input = int(argv[1])
else: #Activates debug mode if sys.argv[1] == "True"
    input = bool(argv[1])


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
while m < n:
    if rank == 0:
        if m!= 0:
            Ab[m-1:, :] = new_Ab
            print("\nStep {} ===> Matrix A:\n{}".format(m+1, Ab[:, :n]))
            print("\nStep {} ===> Matrix b:\n{}\n".format(m+1, Ab[:, n]))
            
            if m<n-1:
                if Ab[m, m] < 0.000001 or Ab[m, m] == 0:
                    print("====> Problematic value ({}) at ({},{})! \n====> Partial pivoting line {}".format(Ab[m, m], m, m, m+1))
                    Ab[[m, m+1], :] = Ab[[m+1, m], :] #The submatrix of rows [m, m+1] is pivoted with the submatrix [m+1, m]


        if m<n-1:
            prev_line = Ab[m]

        recvbuf_supp = np.array_split(Ab[m:, :], size)
        for i in range(len(recvbuf_supp)): # Using len(recvbuf_supp) (which is the same as the number of processes) for better comprehension
            if i == 0:
                count = recvbuf_supp[0].shape[0]*recvbuf_supp[0].shape[1]
            else:
                count = np.hstack([count, recvbuf_supp[i].shape[0]*recvbuf_supp[i].shape[1]])
        displ = [sum(count[:p]) for p in range(size)] # It's the displacement array, i.e, stores the index where the block of data starts in each process
        displ = np.array(displ)

        for p in range(size):
            comm.send(recvbuf_supp[p].shape[0], dest = p, tag = 1) #Number of lines per process of new array (non divisible by # of processes)

        sendbuf = Ab[m:, :]

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
    #print(new_recvbuf, rank, m, new_recvbuf.shape)

    if rank == 0:
        for j in range(1, vpp): #Lines
            ratio = new_recvbuf[j][m]/prev_line[m]
            
            for k in range(n+1): #Columns
                new_recvbuf[j][k] = new_recvbuf[j][k] - ratio * prev_line[k]
    else:
        for j in range(vpp): #Lines
            ratio = new_recvbuf[j][m]/prev_line[m]
            
            for k in range(n+1): #Columns
                new_recvbuf[j][k] = new_recvbuf[j][k] - ratio * prev_line[k]

    #print("Step {} Rank {}: Results: \n{}".format(m, rank, new_recvbuf))
    # print(count-1, sum(count-1)//n) #Needs to be divided by number 
    # print(n-m)
    new_Ab = np.empty([n-m, n+1], dtype = 'float') #The number of lines of the new_A always reduces by one (pivot line that's broadcasted)
    comm.Gatherv(new_recvbuf, [new_Ab, count, displ, MPI.DOUBLE], root = 0)
    #if rank == 0: print("Step {}: New A: \n{}\n".format(m, new_A))   
    
    m += 1

if rank == 0:
    # Backward Substitution
    a = np.array(Ab[:, :n])
    b = np.array(Ab[:, n])
    # print("This is b", b, rank)
    # print("This is a", a, rank)
    x = np.zeros_like(b)
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - sum(a[i][j] * x[j] for j in range(i + 1, n))) / a[i][i]

    print("The final solution is: \nx1: {} \nx2: {} \nx3: {}".format(x[0], x[1], x[2]))

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