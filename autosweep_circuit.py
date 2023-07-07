
import numpy as np


def mark_adjacent_ai_copy(board, clicked, adjacent):
    marks = np.zeros(shape=board.shape)
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            if clicked[i, j] == 1:
                unopened_squares, count_closed, count_marked = get_unopened_indices(clicked, i, j)
                if count_closed != 0:
                    # There are squares around it, we make XORs
                    xor_block = create_XOR_block(clicked, adjacent, i, j)
                    collapsed = collapse_XOR_block(xor_block)
                    for square in collapsed:
                        if square[0] == True:
                            # is bomb
                            marks[square[1][0], square[1][1]] = 2
                        else:
                            # no bomb
                            marks[square[1][0], square[1][1]] = 1
    return marks


def mark_adjacent_ai(board, clicked, adjacent):
    marks = np.zeros(shape=board.shape)

    xor_blocks = []
    common_pairs = []
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            if clicked[i, j] == 1:
                unopened_squares, count_closed, count_marked = get_unopened_indices(clicked, i, j)
                if count_closed != 0:
                    # There are squares around it, we make XORs
                    xor_block = create_XOR_block(clicked, adjacent, i, j)
                    xor_blocks.append(xor_block)
                    common_pairs += get_common_pairs(xor_block)
    
    # Blocks and pairs have been found. I can now iterate through each xor block, make sure it aligns with pairs, and then cancel it out and make marks
    for xor_block in xor_blocks:
        for pair in common_pairs:
            # Iterates for each pair-block combination.
            unopened_squares, count_closed, count_marked = get_unopened_indices(clicked, i, j)
            remove_incompatible_entries(xor_block, pair, unopened_squares)
        collapsed = collapse_XOR_block(xor_block)
        for square in collapsed:
            if square[0] == True:
                # is bomb
                marks[square[1][0], square[1][1]] = 2
            else:
                # no bomb
                marks[square[1][0], square[1][1]] = 1
    return marks



"""
Function will take a board and an open square and then return a list of the "XOR" blocks within it.
An XOR block is a list full of tuples of the form (Row, Col), which represent where a mine would be
in that block. At the beginning of the XOR block is a list of all of the different squares that are involved in said xor block.
"""
def create_XOR_block(clicked, adjacent, row, col):
    if clicked[row, col] != 1:
        print("Creating an XOR for an unopened block [ILLEGAL]")
    # Grabbing some information about the adjacent squares
    unopened_squares, count_closed, count_marked = get_unopened_indices(clicked, row, col)
    mines_left = adjacent[row, col] - count_marked
    
    if len(unopened_squares) != count_closed:
        print("Error in create_XOR_blocks, disagreement between unopened squares")
    
    xor_block = [unopened_squares]
    xor_block_helper(xor_block, [], unopened_squares, 0, mines_left)

    return xor_block
def xor_block_helper(xor_block, current_built, unopened_squares, position, mines_left):
    if position == len(unopened_squares):
        # Base case, we have reached the end of the recursion.
        xor_block.append(current_built)
        return 
    if position + mines_left < len(unopened_squares):
        # Don't add a mine, re-call the function
        xor_block_helper(xor_block, current_built, unopened_squares, position + 1, mines_left)
    if mines_left > 0:
        # Add a mine, re-call the function
        mine_added = current_built.copy()
        mine_added.append(unopened_squares[position])
        xor_block_helper(xor_block, mine_added, unopened_squares, position + 1, mines_left - 1)
    return
def get_unopened_indices(clicked, row, col):
    indices = []
    count_closed = 0
    count_marked = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            count_closed += count_if_closed(clicked, row + i, col + j)
            count_marked += count_if_marked(clicked, row + i, col + j)
            if (row + i >= 0 and row + i < clicked.shape[0] and col + j >= 0 and col + j < clicked.shape[1] and clicked[row + i, col + j] == 0):
                indices.append((row + i, col + j))
               
    return indices, count_closed, count_marked
def count_if_closed(clicked, row, col):
    if (row >= 0 and row < clicked.shape[0] and col >= 0 and col < clicked.shape[1] and clicked[row, col] == 0):
        return 1
    return 0
def count_if_marked(clicked, row, col):
    if (row >= 0 and row < clicked.shape[0] and col >= 0 and col < clicked.shape[1] and clicked[row, col] == 2):
        return 1
    return 0


"""
Function will input an XOR block and determine if there are any commonalities throughout the whole
block. This function will be called after each creation/simplification of a block to see if any
inferences can be made about the board. It will return a list of tuples of (Mine, (row, col)) 
if there is a commonality (where Mine is a boolean)

If I'm right, implementing just this step is the logical equivalent to only finding "first order"
guaranteed mines and safes.

Once the function is implemented that will cancel commonalities through different XOR groups, this
function should become more powerful
"""
def collapse_XOR_block(xor_block):
    common = []
    unopened_squares = xor_block[0]
    for square in unopened_squares:
        # First val will be true if it is in the first term, false otherwise
        first_val = square in xor_block[1] # True if there is a mine in the first possibility, false otherwise (actual value shouldnt matter)
        constant = True # Test variable, starts as true and will become false if a condition is not met
        for i in range(2, len(xor_block)): #
            if first_val != (square in xor_block[i]):
                constant = False
                break

        if constant:
            common.append((first_val, square))
    return common


"""
This function will note all of the pairs that are consistent throughout an entire XOR group.
If there is a consistent pair, it means that it must be true, and all other XOR groups can be
simplified to reflect that. We can then recollapse the XOR groups and see if we find anything else out
"""
def get_common_pairs(xor_block):
    """
    methodology:
    look @ the first set of the XOR group and find all of the pairs that exist within it -> Eventually I'll make this every group, but thats a bit down the line (and will be spensiveish)
    check if each of those pairs is in each of the next groups and remove them from the possibilities if they won't work out
    """
    pairs = []
    unopened_squares = xor_block[0]
    test_pairs = get_pairs(unopened_squares, xor_block[1])
    for pair in test_pairs:
        constant = True
        for i in range(2, len(xor_block)):
            # Iterates through each combination within the block for each pair of concern
            if contains_pair(xor_block[i], pair) != pair[0]:
                constant = False
                break
        if constant:
            pairs.append(pair)
    return pairs


def contains_pair(combination, pair):
    contains = False

    if ((pair[1][1] in combination) == pair[1][0]) and ((pair[2][1] in combination) == pair[2][0]):
        contains = True

    return contains

"""
Function will remove the entries from an xor_block that do not match with the common pairs.
The contains pair function should make this relatively easu
"""
def remove_incompatible_entries(xor_block, pair, scope):
    copy = list(xor_block)
    
    for i in range(1, len(xor_block)):
        #print("Scope: " + str(scope))
        #print("Block: " + str(copy[i]) + ", Pair: " + str(pair))
        if (contains_pair(copy[i], pair) != pair[0]) and (pair[1][1] in scope) and (pair[2][1] in scope):
            xor_block.remove(copy[i])
            #print("Removed!")
        #print("")



"""
Pairs will be defined as a (In, (Mine, First), (Mine, Second)), where In is a boolean representing whether the pair is "in" or "out" of the XOR group.
I will find all of the pairs both in and out of the first entry and then continue checking through the rest of the XOR group.
If they ever disagree with the first entry, then they will be removed from the list
"""
def get_pairs(unopened, first_comb):
    pairs = []
    for i in range(len(unopened)):
        # Iterates for each unopened square. I can make a group with each subsequent square to show the combination
        for j in range(i + 1, len(unopened)):
            # Iterates for each unique combination of squares. I then need to catalogue each one is "in" and "out"
            first_in = (unopened[i] in first_comb)
            second_in = (unopened[j] in first_comb)
            pairs.append((True, (first_in, unopened[i]), (second_in, unopened[j])))
            pairs.append((False, (not first_in, unopened[i]), (second_in, unopened[j])))
            pairs.append((False, (first_in, unopened[i]), (not second_in, unopened[j])))
            pairs.append((False, (not first_in, unopened[i]), (not second_in, unopened[j])))
    return pairs

