from mpi4py import MPI
import numpy as np

# Get the rank and size of the MPI communicator
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Define the matrix and the right-hand side of the system
A = np.array([[2, 2, 1, 1], [1, -3, 2, 3], [-1, 1, -1, -1], [1, -1, 1, 2]], dtype = 'float')
b = np.array([5, 2, -1, 2], dtype = 'int').reshape(1, 4)

# Perform Gaussian elimination without pivoting
for k in range(0, size):
    if rank == k:
        # Compute the multipliers
        multipliers = A[k+1:, k] / A[k, k]
        # Update the matrix and the right-hand side
        A[k+1:, k:] = A[k+1:, k:] - np.outer(multipliers, A[k, k:])
        b[k+1:] = b[k+1:] - multipliers * b[k]
    print(A[k+1:, k:], A[k+1:, k:].shape)
    print(b[k+1:], b[k+1:].shape)
    # Send the updated rows to all other processors
    comm.Bcast(A[k+1:, k:], root=k)
    comm.Bcast(b[k+1:], root=k)

# Solve the system using back-substitution
x = np.zeros(size)
for k in range(size-1, -1, -1):
    if rank == k:
        x[k] = (b[k] - np.dot(A[k, k+1:], x[k+1:])) / A[k, k]
    # Broadcast the solution to all other processors
    comm.Bcast(x[k], root=k)

print(f"Rank {rank}: x = {x}")