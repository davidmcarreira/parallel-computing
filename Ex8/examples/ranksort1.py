from random import random
from sys import argv

n = int(argv[1])
debug = argv[1][0] == '+'

a = [random() for i in range(n)]
b = n*[None]

for i in range(n):
    x = 0
    for j in range(n):
        if a[i] > a[j]:
            x += 1
    b[x] = a[i]

if debug:
    print (', '.join(("%5.3f" % x) for x in a))
    print (', '.join(("%5.3f" % x) for x in b))

