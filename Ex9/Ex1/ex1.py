"""

For the full automatic game experience (or debug) just uncomment the corresponding prints 

"""

import json
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
f = open('nim.json')
rl_stat = json.load(f)
f.close()

rl_stat = convert_json_keys_to_int(rl_stat) # Converting the key values from the json file from str to int

if len(sys.argv) > 1:
	maxpos   = int(sys.argv[1])
	nr_games = int(sys.argv[2])
else:
	maxpos   = int(input('Number of inicial pieces: '))
	nr_games = int(input('Number of games to play: '))

Stat={} # Dictionary composed of 2 sub-dictionaries that store all the statistics of the games (position->move)
for i in range(1,maxpos+1): # Positions
	Stat[i] = {}
	for j in range(1,min(i,3)+1): # Possible noves
		Stat[i][j] = 0

for g in range(nr_games):
	moves = {} # Dictionary to store the moves from each player
	for i in range(1,2+1): # Cycle that fills the moves dictionary with all the possibilities per player
		moves[i] = {}

	# Start position, player 1 is starting
	pos = maxpos
	player = 0
	idx = 0 # Game Round
	while pos:
		# Switch to other player
		player = 2 if player == 1 else 1

		#Game prints
		#print("\nGame {} Round {}".format(g, idx+1))
		#print("Starting pieces: ", pos)

		# Finding the key with highest score
		move = max(Stat[pos], key=Stat[pos].get)

		#Game print
		#print("Player {} took {} pieces.".format(player, move))

		moves[player][pos] = move # Updating the move for the corresponding player
		pos -= move # Updating the position

		#Game prints
		#print("Remaining pieces: ", pos)

		idx += 1

	#Game prints
	#print("\n====> Player {} won!\n".format(player))
	#print("="*90)

	# Last player wins, collect statistics:  
	for pos in moves[player]:
		Stat[pos][moves[player][pos]] += 1 # Increase the score of the winning moves
	# Switch to other player that lost:
	player = 2 if player == 1 else 1
	for pos in moves[player]:
		Stat[pos][moves[player][pos]] -= 1 # Decrease the score of the winning moves

rl_best = {i:max(rl_stat[i], key = rl_stat[i].get) for i in range(maxpos, 0, -1)} # Winning Strategy based on the Reinforcement Learning
stat_best = {i:max(Stat[i], key = Stat[i].get) for i in range(maxpos, 0, -1)} # Learned strategy for a certain number of games

#Debug prints
#print("The correct strategy is (based on training): \n{}".format(rl_best))
#print("The strategy learned is: \n{}".format(stat_best))

for (i, j), (i2, j2) in zip(rl_best.items(), stat_best.items()):
	if j != j2:
		print("\nFor {} games with {} initial pieces:".format(nr_games, maxpos))
		print("- At position {} the winner strategy fails! The correct move for position {} is {} and the move selected was {}.".format(i, i2, j2, j))
		break

"""

After training the nimp.py script for 1000 pieces and 1e6 games, if we play the game with 1000 pieces the results are as follows:

- For 10 games:
	- At position 1000 the winner strategy fails! The correct move for position 1000 is 1 and the move selected was 3.

- For 100 games:
	- At position 1000 the winner strategy fails! The correct move for position 1000 is 1 and the move selected was 3.

- For 1000 games:
	- At position 1000 the winner strategy fails! The correct move for position 1000 is 1 and the move selected was 3.

- For 10000 games:
	- At position 999 the winner strategy fails! The correct move for position 999 is 2 and the move selected was 3.

"""