import random
import numpy as np

def count_adjacent_mines(board, row, col):
    top = bottom = left = right = False
    count = 0
    if (board[row, col] == 1):
        count = count + 1
    if (row > 0):
        bottom = True
        if (board[row - 1, col]):
            count = count + 1
    if (row < board.shape[0] - 1):
        top = True
        if (board[row + 1, col]):
            count = count + 1
    if (col > 0):
        left = True
        if (board[row, col - 1]):
            count = count + 1
    if (col < board.shape[1] - 1):
        right = True
        if (board[row, col + 1]):
            count = count + 1
    
    if top and left and board[row + 1, col - 1]:
        count = count + 1
    if top and right and board[row + 1, col + 1]:
        count = count + 1
    if bottom and left and board[row - 1, col - 1]:
        count = count + 1
    if bottom and right and board[row -1, col + 1]:
        count = count + 1
    return count


# Clicks the square. Returns 1 on a loss, 0 on not a loss
def click_square(board, clicked, row, col):
    if (not (row < 0 or row > board.shape[0] - 1 or col < 0 or col > board.shape[1] - 1) and clicked[row, col] == 0):
        # Uncovers the Square
        clicked[row, col] = 1

        if board[row, col] == 1:
           return 1

        if count_adjacent_mines(board, row, col) == 0:
            click_square(board, clicked, row + 1, col + 1)
            click_square(board, clicked, row + 1, col)
            click_square(board, clicked, row + 1, col - 1)
            click_square(board, clicked, row, col + 1)
            click_square(board, clicked, row, col - 1)
            click_square(board, clicked, row - 1, col + 1)
            click_square(board, clicked, row - 1, col)
            click_square(board, clicked, row - 1, col - 1)
    return 0

        
def generate_board(size, mine_count):
    board = np.zeros(shape=size)
    while (mine_count > 0):
        row = random.randint(0, size[0] - 1)
        col = random.randint(0, size[1] - 1)

        if (board[row, col] == 0):
            board[row, col] = 1
            mine_count = mine_count - 1

    return board


def handle_first_click(board, row, col, size, mine_count):
    while count_adjacent_mines(board, row, col) != 0:
        board = generate_board(size, mine_count)
    return board

def get_number(num, font):
    if num == 1:
        img = font.render(str(num), True, (0, 0, 255))
    elif num == 2:
        img = font.render(str(num), True, (0, 100, 0))
    elif num == 3:
        img = font.render(str(num), True, (200, 0, 0))
    elif num == 4:
        img = font.render(str(num), True, (20, 20, 150))
    elif num == 5:
        img = font.render(str(num), True, (0, 50, 0))
    elif num == 6:
        img = font.render(str(num), True, (100, 0, 0))
    elif num == 7:
        img = font.render(str(num), True, (30, 30, 100))
    elif num == 8:
        img = font.render(str(num), True, (0, 50, 0))
    return img

def load_adjacents(board, size):
    adjacent = np.zeros(shape=size, dtype=np.uint8)
    for i in range(size[0]):
        for j in range(size[1]):
            adjacent[i, j] = count_adjacent_mines(board, i, j)
    return adjacent