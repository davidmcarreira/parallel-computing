from random import random
from sys import argv

n = 1000
debug = argv[1][0] == '+'

a = [random() for i in range(n)]

if debug:
    print (', '.join(("%5.3f" % x) for x in a))

for i in range(n):
    for j in range(i+1,n):
        if a[i] > a[j]:
            a[i], a[j] = a[j], a[i]

if debug:
    print (', '.join(("%5.3f" % x) for x in a))

