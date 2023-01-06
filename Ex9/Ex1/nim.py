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

# if present, use arguments in call: python nim.py {maxpos} {nr_games} 
if len(sys.argv) > 1:
	maxpos   = int(sys.argv[1])
	nr_games = int(sys.argv[2])
else:
	maxpos   = int(input('Number of inicial peaces: '))
	nr_games = int(input('Number of games to play: '))


# Stat:
# two-dimensional dictionary holding the statistical analysis of each move
# Stat[position][move], initialized with 0
# For each simulated game:
# - gains one point if move at position ended in winning the game
# - looses one point if move at position ended in loosing the game

Stat={} # Dictionary composed of 2 sub-dictionaries that store all the statistics of the games (position->move)
for i in range(1,maxpos+1): # Positions
	Stat[i] = {}
	for j in range(1,min(i,3)+1): # Possible noves
		Stat[i][j] = 0

for g in range(nr_games):
	print("Progress: ", g)
	moves = {} # Dictionary to store the moves from each player
	for i in range(1,2+1): # Cycle that fills the moves dictionary with all the possibilities per player
		moves[i] = {}

	# Start position, player 1 is starting
	pos = maxpos
	player = 0
	while pos:
    	# Switch to other player
		player = 2 if player == 1 else 1

		# Finding the key with highest score
		move = max(Stat[pos], key=Stat[pos].get)

		moves[player][pos] = move # Updating the move for the corresponding player

		pos -= move # Updating the position

	# Last player wins, collect statistics:  
	for pos in moves[player]:
		Stat[pos][moves[player][pos]] += 1 # Increase the score of the winning moves
	# Switch to other player that lost:
	player = 2 if player == 1 else 1
	for pos in moves[player]:
		Stat[pos][moves[player][pos]] -= 1 # Decrease the score of the winning moves

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
f = open('nim.json', 'w')
json.dump(Stat, f, sort_keys=True, indent=4, separators=(',', ': '))
f.close()

print("\n" + "="*60 + " Exercise 9.1 (Single Row Nim Game - Reinforcement Learning) " + "="*60)