import numpy as np
from sys import argv

n = int(argv[1])
debug = True

a = np.random.rand(n)
r = np.empty(n, dtype=int)

for i in range(n):
    x = 0
    for j in range(n):
        if a[i] > a[j]:
            x += 1
    r[i] = x

b = np.empty(n, dtype=float)
for i in range(n):
    b[r[i]] = a[i]

if debug:
    print (', '.join(("%5.3f" % x) for x in a))
    print (', '.join(("%5d" % x) for x in r))
    print (', '.join(("%5.3f" % x) for x in b))

