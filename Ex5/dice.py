#Class to create dices and sum of dice throws
class dice:
    
    def __init__(self, sides=6, n_dice=2):
        """
        
        If no parameters are passed to the class, it defaults to 6 sides
        and 2 dices.

        """
        self.sides = sides
        self.n_dice = n_dice
        self.D = {}
        self.min = self.n_dice #Minimum possible sum
        self.max = (self.n_dice*self.sides) #Maximum possible sum
 

    def myDice(self): #Creates a nested dictionary of dices
        for i in range(1, (self.n_dice+2)):
            self.D[i] = {}
            if i <= self.n_dice: #Routine to create the dices
                for j in range(1, (self.sides)+1):
                    self.D[i][j] = 0
            else: #Routine to create the sum dictionary
                for j in range(self.n_dice, (self.n_dice*self.sides)+1):
                    self.D[i][j] = 0
        return self.D