import numpy as np

y = []
y2 = []  
grid = 8 #grid dimension
gpp = grid/4 #grid boxes per process
step = 1/grid
#step = 2/grid #dimension of each grid box


for rank in range(0, 4):
    for j in np.arange(step/2+rank*gpp*step, (rank*gpp*step)+gpp*step, step):
        y2.append(j)
        print("For rank {} the j is {}".format(rank, j))
    print("\n")
print(y2, len(y2))

# for rank in range(0, 4):
#     for j in np.arange((-1+(step/2))+rank*gpp*step, ((-1+(step/2))+rank*gpp*step)+gpp*step, step):
#         y2.append(j)
#         print("For rank {} the j is {}".format(rank, j))
#     print("\n")
# print(y2, len(y2))

#x = np.arange(-1+(step/2), 1+(step/2), step)
x = np.arange((step/2), 1+(step/2), step)
print(list(j for j in x), len(x))