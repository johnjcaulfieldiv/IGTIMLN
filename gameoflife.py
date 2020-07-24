"""

CONWAY'S GAME OF LIFE - RULES

Any live cell with two or three live neighbours survives.
Any dead cell with three live neighbours becomes a live cell.
All other live cells die in the next generation. Similarly, all other dead cells stay dead.

"""

# TODO
# save/load using file
# command line options
# DONE run n iterations
# DONE add history to go forward/back generations
# try cacheing all neighbors for each cell to speed up update()ing

import os
import time
import random

class Life():
    def __init__(self, height=20, width=24):
        self.height = height
        self.width = width
        self.cells = ['*'] * self.height * self.width
        self.history = []
        self.history_index = -1
        self.neighbors = []
        self.setup_neighbors()

    def sizeof_neighbors(self):
        count = 0
        for group in self.neighbors:
            for item in group:
                count += 1
        return count

    def update(self):
        "sets each cell as alive or dead following game rules"
        self.cells = ['*' if self.lives(cell, index) else ' ' for index, cell in enumerate(self.cells)]
        if self.history_index != len(self.history)-1:
            self.history = self.history[:self.history_index+1]
        self.history.append(self.cells)
        self.history_index += 1
    
    def lives(self, cell, index):
        """ Returns True if cell is living or False if cell is dead based on living neighbors """
        living_neighbors = 0
        for n in self.neighbors[index]:
            if self.cells[n] == '*':
                living_neighbors += 1
        return (cell == '*' and (living_neighbors == 2 or living_neighbors == 3) or
                cell == ' ' and living_neighbors == 3)

    def setup_neighbors(self):
        for index in range(len(self.cells)):
            self.neighbors.append([])
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if x == 0 and y == 0:
                        continue
                    row = ((index + self.width * x) % len(self.cells)) // self.width
                    neighbor = (index + y) % self.width + row * self.width
                    self.neighbors[index].append(neighbor)

    def get_neighbor_counts(self, index):
        alive = 0
        dead = 0
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                row = ((index + self.width * x) % len(self.cells)) // self.width
                neighbor = (index + y) % self.width + row * self.width
                if self.cells[neighbor] == '*':
                    alive += 1
                else:
                    dead += 1
        return alive, dead

    def get_past_state(self, n=1):
        """ Returns nth state back from current if exists, else None """
        if self.history_index - n < 0:
            return None
        return self.history[self.history_index-n]

    def rewind_state(self, amount=1):
        """ Sets cells to previous state. Returns True on success, False if no history """
        if self.history_index - amount < 0:
            return False
        self.history_index -= amount
        self.cells = self.history[self.history_index]
        return True

    def foward_state(self, amount=1):
        """ Sets cells to next state. Returns True on success, False if no next state """
        if self.history_index + amount >= len(self.history):
            return False
        self.history_index += amount
        self.cells = self.history[self.history_index]
        return True

    def rewind_to_first(self):
        self.history_index = 0
        self.cells = self.history[self.history_index]

    def forward_to_last(self):
        self.history_index = len(self.history)-1
        self.cells = self.history[self.history_index]

    def randomize(self, perc):
        "Sets perc % of the cells in the grid as alive (roughly)"
        self.cells = list(map(lambda c: '*' if random.randint(1,100) <= perc else ' ', self.cells))
        self.history = []
        self.history_index = 0
        self.history.append(self.cells)

    def print_grid(self):
        "Print the current state to console"
        grid = ""
        for cell in [c + "\n" if (i+1) % self.width == 0 else c + " " for i, c in enumerate(self.cells)]:
            grid += cell
        print(grid)

    def is_looping(self):
        return (len(self.history) >= 3 and
                (self.history[-1] == self.history[-2] or
                self.history[-1] == self.history[-3]))

    def print_all(self):
        all =  "height:     {}\n".format(self.height)
        all += "width:      {}\n".format(self.width)
        all += "len(cells): {}\n".format(len(self.cells))
        all += "len(cache): {}".format(self.sizeof_neighbors())
        print(all)

    def start(self):
        self.randomize(50)
        response = ""
        while (not response.startswith("e")):
            os.system('cls')
            self.print_grid()
            response = input("\nNext? > ").lower()
            self.update()

    def auto(self, timestep=.5):
        generation = 1
        self.randomize(70)
        while (True):
            os.system('cls')
            print()
            self.print_grid()
            print("\nGeneration: " + str(generation))
            generation += 1
            self.update()
            time.sleep(timestep)

    def REPL_print_grid(self):
        os.system('cls')
        print()
        self.print_grid()
        print("\nGeneration: " + str(self.history_index+1))

    def REPL(self):
        response = ""
        while not response.startswith("q"):
            response = input("[b]ack, [f]orward, [s]tart, [e]nd, [q]uit >> ").lower()
            if response.startswith('b'):
                if self.rewind_state():
                    self.REPL_print_grid()
                else:
                    print("Already at first generation")
            if response.startswith('f'):
                if self.foward_state():
                    self.REPL_print_grid()
                else:
                    print("Already at final generation")
            if response.startswith('s'):
                self.rewind_to_first()
                self.REPL_print_grid()
            if response.startswith('e'):
                self.forward_to_last()
                self.REPL_print_grid()
            if response.startswith('p'): # print info
                self.print_all()
            if response.startswith('a'): # run it back! [a]gain!
                main()
                return

    def auto_detect_loop(self, perc=0.5, timestep=.5):
        # run the game
        self.randomize(perc)
        while (not self.is_looping()):
            self.REPL_print_grid()
            self.update()
            time.sleep(timestep)
        print("Current state is in infinite loop. Terminated.")
        # start a REPL to view game states
        self.REPL()

    def auto_finish(self, perc=0.5):
        # run the game without any ui until a loop is found
        self.randomize(perc)
        while (not self.is_looping()):
            os.system('cls')
            print()
            print("Running out the game. Gen " + str(self.history_index+1))
            self.update()
        self.REPL_print_grid()
        # start a REPL to view game states
        self.REPL()

    def auto_n_generations(self, n=500, perc=0.5):
        # run the game without any ui until a loop is found or n gens pass
        self.randomize(perc)
        while (n > 1 and not self.is_looping()):
            #n -= 1
            #os.system('cls')
            #print()
            #print("Running out the game. Gen " + str(self.history_index+1))
            self.update()
        self.REPL_print_grid()
        # start a REPL to view game states
        self.REPL()

def main():
    #runtests()
    #Life(55,80).auto_detect_loop(80, .1) # large, good for ogling
    #Life(5,5).auto_detect_loop(60, .1)  # small, good for testing
    #Life(55,80).auto_finish(50)
    Life(60,60).auto_n_generations(5000, 50)

if __name__ == "__main__":
    main()
















#   def test_check_neighbors(l, verbose=True):
#   if verbose: 
#       print(l.check_neighbors(1))
#   assert l.check_neighbors(1) == set([70,71,72,0,2,10,11,12]) # top row
#   if verbose: 
#       print(l.check_neighbors(0))
#   assert l.check_neighbors(0) == set([79,70,71,9,1,19,10,11]) # corner top left
#   if verbose: 
#       print(l.check_neighbors(2))
#   assert l.check_neighbors(2) == set([71,72,73,1,3,11,12,13]) # top row
#   if verbose: 
#       print(l.check_neighbors(9))
#   assert l.check_neighbors(9) == set([78,79,70,8,0,18,19,10]) # corner top right
#   if verbose: 
#       print(l.check_neighbors(70))
#   assert l.check_neighbors(70) == set([69,60,61,79,71,9,0,1]) # corner bot left
#   if verbose: 
#       print(l.check_neighbors(55))
#   assert l.check_neighbors(55) == set([44,45,46,54,56,64,65,66]) # center
#   if verbose: 
#       print(l.check_neighbors(79))
#   assert l.check_neighbors(79) == set([68,69,60,78,70,8,9,0]) #corner bot right
#   if verbose: 
#       print(l.check_neighbors(72))
#   assert l.check_neighbors(72) == set([61,62,63,71,73,1,2,3]) # bot row
#   if verbose: 
#       print(l.check_neighbors(10))
#   assert l.check_neighbors(10) == set([9,0,1,19,11,29,20,21]) # left col
#   if verbose: 
#       print(l.check_neighbors(59))
#   assert l.check_neighbors(59) == set([48,49,40,58,50,68,69,60]) # right col
#   print("All tests passed")

# def runtests():
#   my_life = Life(8,10)
#   try:
#       test_check_neighbors(my_life, False)
#   except:
#       test_check_neighbors(my_life)