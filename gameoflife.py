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
# DONE try cacheing all neighbors for each cell to speed up update()ing

import os
import time
import random
import timeit


class Life():
    def __init__(self, height=20, width=24):
        self.height = height
        self.width = width
        self.cells = ['*'] * self.height * self.width
        self.history = []
        self.history_index = -1
        self.neighbors = []
        self.cache_neighbors()

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
        "Returns True if cell is living or False if cell is dead based on living neighbors"
        living_neighbors = 0
        for n in self.neighbors[index]:
            if self.cells[n] == '*':
                living_neighbors += 1
        return (cell == '*' and (living_neighbors == 2 or living_neighbors == 3) or
                cell == ' ' and living_neighbors == 3)

    def cache_neighbors(self):
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
        "Returns nth state back from current if exists, else None"
        if self.history_index - n < 0:
            return None
        return self.history[self.history_index-n]

    def rewind_state(self, amount=1):
        "Sets cells to previous state. Returns True on success, False if no history"
        if self.history_index - amount < 0:
            return False
        self.history_index -= amount
        self.cells = self.history[self.history_index]
        return True

    def foward_state(self, amount=1):
        "Sets cells to next state. Returns True on success, False if no next state"
        if self.history_index + amount >= len(self.history):
            return False
        self.history_index += amount
        self.cells = self.history[self.history_index]
        return True

    def set_state(self, n):
        "Sets cells to generation n and returns True on success, False on n OoB"
        n -= 1
        if n < 0 or n >= len(self.history):
            return False
        self.history_index = n
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

    def print_all_oneline(self):
        all =  "height:     {} ".format(self.height)
        all += "width:      {} ".format(self.width)
        all += "len(cells): {} ".format(len(self.cells))
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
            response = input("[b]ack, [f]orward, [s]tart, [e]nd, [q]uit >> ").lower().strip()
            try:
                index = int(response)
                if self.set_state(index):
                    self.REPL_print_grid()
                else:
                    print("There is no generation " + response)
            except:
                pass
            if response.startswith('b'):
                if self.rewind_state():
                    self.REPL_print_grid()
                else:
                    print("Already at first generation")
            elif response.startswith('f'):
                if self.foward_state():
                    self.REPL_print_grid()
                else:
                    print("Already at final generation")
            elif response.startswith('s'):
                self.rewind_to_first()
                self.REPL_print_grid()
            elif response.startswith('e'):
                self.forward_to_last()
                self.REPL_print_grid()
            elif response.startswith('p'): # print info
                self.print_all()
            elif response.startswith('a'): # run it back! [a]gain!
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
        print("Running out the game...")
        while (not self.is_looping()):
            self.update()
        self.REPL_print_grid()
        # start a REPL to view game states
        self.REPL()

    def auto_n_generations(self, n=500, perc=0.5):
        # run the game without any ui until a loop is found or n gens pass
        self.randomize(perc)
        print("Running out the game...")
        while (n > 1 and not self.is_looping()):
            #n -= 1
            #os.system('cls')
            #print()
            #print("Running out the game. Gen " + str(self.history_index+1))
            self.update()
        self.REPL_print_grid()
        # start a REPL to view game states
        self.REPL()

    def sim(self, perc, max):
        "Gives metrics"
        start = timeit.default_timer()
        self.randomize(perc)
        while (self.history_index < max and not self.is_looping()):
            self.update()
        elapsed = timeit.default_timer() - start
        self.print_all()
        print("time:       {}s".format(elapsed))
        print("perc:       {}".format(perc))
        print("gens:       {}\n".format(self.history_index+1))

    def sim_oneline(self, perc, max):
        "Gives metrics on one line"
        start = timeit.default_timer()
        self.randomize(perc)
        while (self.history_index < max and not self.is_looping()):
            self.update()
        elapsed = timeit.default_timer() - start
        print("time:       {}s ".format(elapsed), end='')
        print("perc:       {} ".format(perc), end='')
        print("gens:       {} ".format(self.history_index+1), end='')
        self.print_all_oneline()
        print()


def main():
    #runtests()
    #Life(55,80).auto_detect_loop(80, .1) # large, good for ogling
    #Life(5,5).auto_detect_loop(60, .1)  # small, good for testing
    #Life(55,80).auto_finish(50)
    Life(60,60).auto_n_generations(5000, 40)
    #for x in range(1, 101):
    #    Life(60,60).sim_oneline(x, 5000)


if __name__ == "__main__":
    main()
