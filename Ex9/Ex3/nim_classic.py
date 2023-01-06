import json, sys
import random

# if present, use arguments in call: python nim.py {maxpos} {nr_games} 
if len(sys.argv) > 1:
    nr_games = int(sys.argv[1])
else:
    nr_games = int(input('Number of games to train: '))

game_heaps = [1, 3, 5, 7]
Stat={} # Dictionary composed of 2 sub-dictionaries that store all the statistics of the games (heap->position->move)
for i in game_heaps: # Heaps
    Stat[i] = {}
    for j in range(1,i+1): # Position according to the heap
        Stat[i][j] = {}
        for k in range(1,min(j,3)+1): # Possible noves
            Stat[i][j][k] = 0

    # print(Stat[i])

for g in range(nr_games):
    print("Progress: ", g)
    heaps = [1, 3, 5, 7] # List that keeps score of which heaps are still playable
    moves = {} # Dictionary to store the moves from each player
    for i in range(1,2+1): # Cycle that fills the moves dictionary with all the possibilities per player
        moves[i] = {}
        for j in heaps:
            moves[i][j] = {}

    # Start position, player 1 is starting
    player = 0
    while True:

        # Finding the heap key with highest score
        max_value = float('-inf') # Initialize a variable to store the key of the outer dictionary where the max value is found
        heap = None
        keys = [i for i in heaps if i!=0]
        for outermost_key, outermost_dict in {k: Stat[k] for k in keys}.items(): # Iterate over the heap's dictionaries
            for outer_key, outer_dict in outermost_dict.items(): # Iterate over the position's dictionaries
                for value in outer_dict.values(): # Iterate over the move's dictionaries and find the one with higher score
                    # Update the maximum value and the key if necessary
                    if value > max_value:
                        max_value = value # Save the maximum value
                        heap = outermost_key # Save the key, i.e heap, where that occurs
        idx = 0 # Game Round
        pos = heap # The positions will depend of the heap being played
        heap_idx = heaps.index(heap) # Current heap
        while True:
            # Switch to other player
            player = 2 if player == 1 else 1
            
            #print("\nHeap {} for game {} and position {}".format(heap, g, pos))
            move = [keys for keys,values in Stat[heap][pos].items() if values == max(Stat[heap][pos].values())]           
            if len(move) != 1: # This means that there are ambiguous values
                move = move[random.randint(0, len(move)-1)] # When multiple values have the same score, a random choice between them is made
            else:
                move = move[0] # When only value is present, that's the absolute maxium

            moves[player][heap][pos] = move # Updating the move for the corresponding player

            pos -= move # Reducing the number of available pieces
            heaps[heap_idx] -= move # Updating the heaps

            if pos == 0: break # Break when there's no more pieces to take, i.e pos = 0

            idx += 1 # Increasing the game round
        if all(item == 0 for item in heaps): break # All the heaps are cleared, so the game is finished
    
    # Last player wins, collect statistics:
    for heap in moves[player]:
        for pos in moves[player][heap]:
            Stat[heap][pos][moves[player][heap][pos]] += 1 # Increase the score of the winning moves
    # Switch to other player that lost:
    player = 2 if player == 1 else 1
    for heap in moves[player]:
        for pos in moves[player][heap]:
            Stat[heap][pos][moves[player][heap][pos]] -= 1 # Decrease the score of the winning moves

rl = {i:{j:max(Stat[i][j], key = Stat[i][j].get) for j in range(i, 0, -1)} for i in [1, 3, 5, 7]} # Learned strategy for a certain number of games
print("The strategy learned for {} is: \n{}".format(nr_games, rl))

# Save Stat in json file (weights of the learning process):
f = open('nim_classic.json', 'w')
json.dump(Stat, f, sort_keys=True, indent=4, separators=(',', ': '))
f.close()

print("\n" + "="*60 + " Exercise 9.3 (Classic Nim Game - Reinforcement Learning) " + "="*60)

"""

After training the nimp_classic.py script for 1e6 games several times, we conclude the expected: it never converges in an optimal solution
indicating that there's no strategy to win the classic NIM Game!

"""