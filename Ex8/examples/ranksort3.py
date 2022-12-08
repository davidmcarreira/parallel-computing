import numpy as np
from sys import argv

n = int(argv[1])
debug = argv[1][0] == '+'

a = np.random.rand(n)
o = []
r = np.empty(n, dtype=int)
for i in range(n):
    x = 0
    for j in range(n):
        if a[i] > a[j]:
            x += 1
    o.append((i,x))
    r[i] = x

b = n*[None]
for i,x in o:
    b[x] = a[i]

if debug:
    print (', '.join(("%5.3f" % x) for x in a))
    print (', '.join(("%5d" % x) for x in r))
    print (', '.join(("%5.3f" % x) for x in b))

