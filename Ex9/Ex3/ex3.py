"""

For the full automatic game experience (or debug) just uncomment the corresponding prints 

"""


import json
import random
import sys

def convert_json_keys_to_int(json_data):
    # Check if the input is a dictionary
	if isinstance(json_data, dict):
        # Create a new dictionary to store the converted data
		converted_data = {}
        # Iterate over the keys in the dictionary
		for key in json_data.keys():
            # Convert the key to an integer
			int_key = int(key)
            # Recursively convert the value of the key
			value = convert_json_keys_to_int(json_data[key])
            # Add the converted key-value pair to the new dictionary
			converted_data[int_key] = value
        # Return the converted dictionary
		return converted_data
    # If the input is not a dictionary, return it as is
	return json_data


#Loading the previous trained weights
f = open('nim_classic.json')
rl_stat = json.load(f)
f.close()

rl_stat = convert_json_keys_to_int(rl_stat) # Converting the key values from the json file from str to int


if len(sys.argv) > 1:
	nr_games = int(sys.argv[1])
else:
	nr_games = int(input('Number of games to play: '))

game_heaps = [1, 3, 5, 7]
Stat={} # Dictionary composed of 3 sub-dictionaries that store all the statistics of the games (heap->position->move)
for i in game_heaps: # Heaps
	Stat[i] = {}
	for j in range(1,i+1): # Position according to the heap
		Stat[i][j] = {}
		for k in range(1,min(j,3)+1): # Possible noves
			Stat[i][j][k] = 0


for g in range(nr_games):
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
            
			# Game prints
			#print("\nGame {} Round {}".format(g, idx+1))
			#print("Starting heap: ", heaps)

			move = [keys for keys,values in Stat[heap][pos].items() if values == max(Stat[heap][pos].values())]           
			if len(move) != 1: # This means that there are ambiguous values
				move = move[random.randint(0, len(move)-1)] # When multiple values have the same score, a random choice between them is made
			else:
				move = move[0] # When only value is present, that's the absolute maxium
            
			# Game print
			#print("Player {} took {} pieces from heap {}".format(player, move, heap))
			moves[player][heap][pos] = move # Updating the move for the corresponding player

			pos -= move # Reducing the number of available pieces
			heaps[heap_idx] -= move # Updating the heaps
			
			# Game print
			#print("Resulting heap: ", heaps)
			if pos == 0: break # Break when there's no more pieces to take, i.e pos = 0

			idx += 1 # Increasing the game round
		if all(item == 0 for item in heaps):  # All the heaps are cleared, so the game is finished
            # Game print
			#print("\n====> Player {} won!\n".format(player))
			#print("="*90)
			break # All the heaps are cleared
    
    # Last player wins, collect statistics:
	for heap in moves[player]:
		for pos in moves[player][heap]:
			Stat[heap][pos][moves[player][heap][pos]] += 1 # Increase the score of the winning moves
    # Switch to other player that lost:
	player = 2 if player == 1 else 1
	for heap in moves[player]:
		for pos in moves[player][heap]:
			Stat[heap][pos][moves[player][heap][pos]] -= 1 # Decrease the score of the winning moves

rl_best = {i:{j:max(rl_stat[i][j], key = rl_stat[i][j].get) for j in range(i, 0, -1)} for i in [1, 3, 5, 7]} # Winning Strategy based on the Reinforcement Learning
stat_best = {i:{j:max(Stat[i][j], key = Stat[i][j].get) for j in range(i, 0, -1)} for i in [1, 3, 5, 7]} # Learned strategy for a certain number of games

# Debug prints          
# print("The correct strategy is (based on training): \n{}".format(rl_best))
# print("The strategy learned is: \n{}".format(stat_best))

for (i, j), (i2, j2) in zip(rl_best.items(), stat_best.items()): # Determining when the learned strategy differentiates from the correct strategy
	if j != j2:
		print("\nFor {} games:".format(nr_games))
		print("- At position {} the winner strategy fails! The correct move for position {} is {} and the move selected was {}.".format(i, i2, j2, j))
		break

print("\n" + "="*60 + " Exercise 9.3 (Classic Nim Game) " + "="*60)

"""

After training the nimp_classic.py script for 1e6 games several times, we conclude the expected: it never converges in an optimal solution
indicating that there's no strategy to win the classic NIM Game!

"""