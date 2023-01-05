# Simulation of NIM game with one heap of maxpos peaces
# Rule: at each position, take 1, 2 or 3 pieces.
# Winner: the player that takes the last piece.
#
# https://en.wikipedia.org/wiki/Nim
#
# Machine learning:
#   Play nr_games times against yourself and collect
#   statistics for winning and loosing positions,
#   in order to obtain best move for any position.
#


import json, sys
import random
import itertools

# if present, use arguments in call: python nim.py {maxpos} {nr_games} 
if len(sys.argv) > 1:
    maxpos   = sys.argv[1]
    nr_games = sys.argv[2]
else:
    maxpos   = input('Number of inicial peaces: ')
    nr_games = input('Number of games to play: ')
maxpos   = int(maxpos)
nr_games = int(nr_games)

# Stat:
# two-dimensional dictionary holding the statistical analysis of each move
# Stat[position][move], initialized with 0
# For each simulated game:
# - gains one point if move at position ended in winning the game
# - looses one point if move at position ended in loosing the game

Stat={}
for i in [1, 3, 5, 7]: # Heaps
    Stat[i] = {}
    for j in range(1,i+1): # Number of elements
        Stat[i][j] = {}
        for k in range(1,min(j,3)+1): # Moves
            Stat[i][j][k] = 0

    print(Stat[i])

for g in range(nr_games):
    heaps = [1, 3, 5, 7]
    moves = {}
    for i in range(1,2+1):
        moves[i] = {}
        for j in heaps:
            moves[i][j] = {}
    
    print("moves", moves)
    # start position, player 1 is starting

    player = 0
    # perform one game:
    while True:
        
        # Finding the heap key with highest score
        max_value = float('-inf') # Initialize a variable to store the key of the outer dictionary where the max value is found
        heap = None
        keys = [i for i in heaps if i!=0]
        print("keys", keys)
        for outermost_key, outermost_dict in {k: Stat[k] for k in keys}.items():
            #print(outermost_key, outermost_dict)
            for outer_key, outer_dict in outermost_dict.items():
                #print(outer_key, outer_dict)
                for value in outer_dict.values():
                    # update the maximum value and the key if necessary
                    if value > max_value:
                        max_value = value
                        heap = outermost_key

        while True:
            # switch to other player
            player = 2 if player == 1 else 1
            
            pos = heap
            print("Heap {} for game {}".format(heap, g))
            for keys, values in Stat[heap][pos].items():
                if values == max(Stat[heap][pos].values()):
                    move = keys
                else:
                    break

            # if len(move) != 1: # This means that there are ambiguous values
            #     move = move[random.randint(0, len(move)-1)] # When multiple values have the same score, a random choice between them is made
            # else:
            #     move = move[0] # When only value is present, that's the absolute maxium
            #print(pos, move) 

            moves[player][heap][pos] = move
            pos -= move

            print(heaps, heap, move, pos)
            if pos == 0:
                heaps[heaps.index(heap)] -= move
            else:
                heaps[heaps.index(pos)] -= move
            
            if pos == 0: break

        if all(item == 0 for item in heaps): break # All the heaps are cleared
        
    # last player wins, collect statistics:  
    for pos in moves[player]:
        Stat[pos][moves[player][pos]]+= 1
    # switch to other player that lost:
    player = 2 if player == 1 else 1
    for pos in moves[player]:
        Stat[pos][moves[player][pos]] -= 1

# Detect best move for all positions and print statistics:
for i in range(maxpos, 0, -1):
    # get best move (key of highest value in Stat[i])
    best = max(Stat[i], key=Stat[i].get)
    v = Stat[i][best]
    if v<0:
        best = '-'
        v = ''
    print ("%3d: %s %5s     %s" % (i, str(best), str(v), str(Stat[i])))

# Save Stat in json file:
f = open('nim_classic.json', 'w')
json.dump(Stat, f, sort_keys=True, indent=4, separators=(',', ': '))
f.close()