
import numpy as np





# Returns a tuple of (Opened, Marked) to know the state of the game
def count_adjacent_clicked(clicked, row, col):
    count_closed = 0
    count_marked = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            count_closed += count_if_closed(clicked, row + i, col + j)
            count_marked += count_if_marked(clicked, row + i, col + j)
    return count_closed, count_marked
def count_if_closed(clicked, row, col):
    if (row >= 0 and row < clicked.shape[0] and col >= 0 and col < clicked.shape[1] and clicked[row, col] == 0):
        return 1
    return 0
def count_if_marked(clicked, row, col):
    if (row >= 0 and row < clicked.shape[0] and col >= 0 and col < clicked.shape[1] and clicked[row, col] == 2):
        return 1
    return 0

# Mark 1 means safe, mark 2 means Mine
def mark_adjacent_ai(board, clicked, adjacent):
    marks = np.zeros(shape=board.shape)
    for row in range(board.shape[0]):
        for col in range(board.shape[1]):
            if (clicked[row, col] == 1):
                count_closed, count_marked = count_adjacent_clicked(clicked, row, col)
                mines_left = adjacent[row, col] - count_marked
                
                if mines_left == 0 and count_closed != 0:
                    # Can clear all open squares around the boy
                    set_adjacent_safe(marks, clicked, row, col)
                elif mines_left == count_closed and count_closed != 0:
                    # All remaining squares are mines around the boy
                    set_adjacent_mines(marks, clicked, row, col)
    return marks
 
def set_adjacent_safe(marks, clicked, row, col):
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (row + i >= 0 and row + i < clicked.shape[0] and col + j >= 0 and col + j < clicked.shape[1] and clicked[row + i, col + j] == 0):
                marks[row + i, col + j] = 1

def set_adjacent_mines(marks, clicked, row, col):
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (row + i >= 0 and row + i < clicked.shape[0] and col + j >= 0 and col + j < clicked.shape[1] and clicked[row + i, col + j] == 0):
                marks[row + i, col + j] = 2



# Slightly cooler function to do some cool deductions
def smart_ai_mode(board, clicked, adjacent):
    marks = np.zeros(shape=board.shape)
    groups = []
    for row in range(board.shape[0]):
        for col in range(board.shape[1]):
            if (clicked[row, col] == 1):
                count_closed, count_marked = count_adjacent_clicked(clicked, row, col)
                mines_left = adjacent[row, col] - count_marked
                if mines_left == 1:
                    # This is where I can add a group that contains EXACTLY one mine.
                    groups.append(get_unopened_indices(clicked, row, col))
    # Groups now contains all groups with exactly one mine in them
    # For each group, I'm going to find any opened square that might overlap with them
    for x in groups:
        row_min = board.shape[0]; row_max = -1; col_min = board.shape[1]; col_max = -1
        for coordinates in x:
            # This is me finding a row and column envelope for the group so i know where to check
            row_min = min(row_min, coordinates[0])
            row_max = max(row_max, coordinates[0])
            col_min = min(col_min, coordinates[1])
            col_max = max(col_max, coordinates[1])
        # Row/ Col min and max have been set. I will iterate through an envelope of that size + 1 in all directions
        for row in range(max(row_min - 1, 0), min(row_max + 1, board.shape[0] - 1) + 1):
            for col in range(max(col_min - 1, 0), min(col_max + 1, board.shape[1] - 1) + 1):
                # Iterates through each (row, col) of importance
                # Fxn returns the number of parts of the group contained within the squares envelope.
                if clicked[row, col] == 1:
                    contained = square_contains_group(row, col, x)

                    if contained > 1:

                        # When contained is greater than 1, there is some processing to be done! 
                        # This means that more than one "grouped" square is contained within the numbers sphere of influence.
                        # These grouped squares can contain no more than one mine.
                        # This means that the number of mines left will be (at most) one less over the uncontained squares
                        count_closed, count_marked = count_adjacent_clicked(clicked, row, col)
                        mines_left = adjacent[row, col] - count_marked
                        new_closed = count_closed - contained + 1 # over "Contained" fewer unopened squares

                        if mines_left == new_closed: # If there are the same number of mines in the new distribution as there are unopened squares, they must be mines
                            # All remaining squares are mines around the boy
                            set_ungrouped(marks, clicked, row, col, x, False)

                        
                        # statement below's heart is in the right place but nothing else is so (can only cancel out when we contain an entire group) -> guarantees a mine
                        if contained == len(x) and mines_left == 1: # if there are no mines (and unopened squares), set them all safe
                            # Can clear all open squares around the boy (that arent a part of the group)
                            set_ungrouped(marks, clicked, row, col, x, True)
    return marks


def set_ungrouped(marks, clicked, row, col, x, safe):
    for i in range(-1, 2):
        for j in range(-1, 2):
            ungrouped = True
            for coords in x:
                if coords[0] == row + i and coords[1] == col + j: ungrouped = False
            if (ungrouped and row + i >= 0 and row + i < clicked.shape[0] and col + j >= 0 and col + j < clicked.shape[1] and clicked[row + i, col + j] == 0):
                if safe: 
                    marks[row + i, col + j] = 1
                else : 
                    marks[row + i, col + j] = 2


def square_contains_group(row, col, x):
    count = 0
    for coords in x:
        if abs(row - coords[0]) <= 1 and abs(col - coords[1]) <= 1:
            count += 1
    return count


def get_unopened_indices(clicked, row, col):
    indices = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (row + i >= 0 and row + i < clicked.shape[0] and col + j >= 0 and col + j < clicked.shape[1] and clicked[row + i, col + j] == 0):
                indices.append((row + i, col + j))
    return indices