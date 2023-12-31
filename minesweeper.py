import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count & self.count != 0:
            return self.cells
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

        pass

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)

        pass

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the new cell as safe (This function also updates every sentence in the KB.)
        self.mark_safe(cell)

        # 3) A sentence requires a cell and a count, and returns a Sentence with a set of cells with a count
        neighbors = set()

        # First, build the set of neighbors, not including the square itself
        for i in range(cell[0]-1, cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                
                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # If the neighboring cell is on the board, add it to the set
                if 0<= i < self.height and 0 <= j < self.width:
                    neighbors.add((i, j))

        # Create a sentence object and add it to the knowledge list
        sentence = Sentence(neighbors, count)

        """
        Each time we add a sentence, we loop it over every existing sentence.
        Check if the new sentence is a subset of the existing sentence.
        If it is, subtract the new from the old and infer a new sentence.
        This should bake all inferences into the knowledge base.

        Then, for each sentence, check whether we can infer mines or safes.
        If we learn of a new mine or safe coordinate, add it to a set,
        and add them to the AI.
        """

        new_mines = set()
        new_safes = set()
        new_knowledge = []
        
        for fact in self.knowledge:
            if sentence.cells.issubset(fact.cells) and sentence.cells != fact.cells:
                synthesis = Sentence(fact.cells - sentence.cells, fact.count - sentence.count)
                if synthesis not in new_knowledge and synthesis.cells != sentence.cells:
                    new_knowledge.append(synthesis)

            if fact.cells.issubset(sentence.cells) and sentence.cells != fact.cells:
                synthesis = Sentence(sentence.cells - fact.cells, sentence.count - fact.count)
                if synthesis not in new_knowledge and synthesis.cells != sentence.cells:
                    new_knowledge.append(synthesis)

        
        if len(new_knowledge) > 0:
            self.knowledge.extend(new_knowledge)

        # After we're done looping over the knowledge base to look for inferences,
        # we can finally add our sentence to the knowledge base.
        self.knowledge.append(sentence)

        """ Print statements for debugging
        print("New knowledge: ")
        for statement in new_knowledge:
            print(statement)
        print("Knowledge base: ")
        for statement in self.knowledge:
            print(statement)
        End debugging """

        for fact in self.knowledge:
            # Check whether we can infer any mines from the sentence
            known_mines = fact.known_mines()

            if known_mines:
                for known_mine in known_mines:
                    new_mines.add(known_mine)

            known_safes = fact.known_safes()

            if known_safes:
                for known_safe in known_safes:
                    new_safes.add(known_safe)
           
        for new_mine in new_mines:
            self.mark_mine(new_mine)

        for new_safe in new_safes:
            self.mark_safe(new_safe)

        """
        
        print(f" Safe spots: ")
        for safe in self.safes:
            print(safe)

        """

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        while True:
            i = random.randint(0, self.height -1)
            j = random.randint(0, self.width -1)

            attempt = (i, j)

            if attempt not in self.mines and attempt not in self.moves_made:
                return attempt
