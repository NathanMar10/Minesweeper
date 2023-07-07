from turtle import end_fill
import numpy as np
import pygame

from autosweep_circuit import mark_adjacent_ai
from autosweep import smart_ai_mode

from functions import click_square
from functions import generate_board
from functions import handle_first_click
from functions import get_number
from functions import load_adjacents


# GAME CONFIGURATION:
size = (30, 20)
mine_count = 125
curr_mines = mine_count
# GUI Configuration: 
square_size = 25
font_size = 18
restart_size = (200, 50)
restart_font_size = 32

marked_color = (100, 80, 230)
button_color = (180, 180, 180)
mine_color = (230, 80, 100)
clicked_mine_color = (255, 255, 255)

safe_color = (100, 255, 100)
unsafe_color = (255, 100, 100)


# Board stores all of the mines
board = generate_board(size, mine_count)
# Clicked stores where the player has clicked.
# 0 = Unclicked
# 1 = Clicked
# 2 = Marked as a Mine
clicked = np.zeros(shape=size)
adjacent = np.zeros(shape=size)


pygame.init()
pygame.display.set_caption("Betcha can't beat me, Kash!")
screen = pygame.display.set_mode([square_size * size[0], square_size * size[1] + restart_size[1]])
font = pygame.font.Font('freesansbold.ttf', font_size)
restart_font = pygame.font.Font('freesansbold.ttf', restart_font_size)
restart_msg = 'Give Up?'

# State parameters within the game
running = True
game_over = False
first_click = True
won_game = False
ai_enabled = True
ai_moves = True

while running:

    # Event Handler
    for event in pygame.event.get():
        # Handles closing the game
        if event.type == pygame.QUIT:
            running = False

        # Handles player clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = event.pos

            # Checks if the click was on the game board
            if (click_pos[1] > size[1] * square_size):
                if (abs(click_pos[0] - size[0] * square_size / 2) < restart_size[0] / 2):
                    board = generate_board(size, mine_count)
                    clicked = np.zeros(shape=size)
                    first_click = True
                    game_over = False
                    won_game = False
                    restart_msg = "Give Up?"
                    curr_mines = mine_count
            elif not game_over:
                row = int(np.floor(click_pos[0] / square_size))
                col = int(np.floor(click_pos[1] / square_size))

                # If the Click is a Left click
                if event.button == 1:
                    if first_click:
                        first_click = False
                        board = handle_first_click(board, row, col, size, mine_count)
                        adjacent = load_adjacents(board, size)
                    if clicked[row, col] == 0:
                        game_over = click_square(board, clicked, row, col)

                # If the click is a Right Click
                elif event.button == 3: 
                    if clicked[row, col] == 0:
                        clicked[row, col] = 2
                        curr_mines = curr_mines - 1
                    elif clicked[row, col] == 2:
                        clicked[row, col] = 0
                        curr_mines = curr_mines + 1

    # Sets the Background Color
    screen.fill((155, 155, 155))

    # Drawing the Occurs no matter the game state
    for i in range(size[0]):
        for j in range(size[1]):
                if (clicked[i, j] == 1):
                    if (board[i, j]):
                        # Draws Bombs Red
                        pygame.draw.rect(surface=screen, color=clicked_mine_color, rect=(square_size * i, square_size * j, square_size, square_size))
                    else:
                        # Draws Numbers
                        num = adjacent[i, j]
                        if num != 0 and board[i, j] != 1:
                            img = get_number(num, font)
                            screen.blit(img, dest=(square_size * (i) + 8, square_size * (j) + 5))

                elif (clicked[i, j] == 2):
                    pygame.draw.rect(surface=screen, color=marked_color, rect=(square_size * i, square_size * j, square_size, square_size))
                elif (clicked[i, j] == 0):   
                    pygame.draw.rect(surface=screen, color=button_color, rect=(square_size * i, square_size * j, square_size, square_size))

    # Drawing for the end of the game. This uncovers mines and shows false flags
    if game_over:
        for i in range(size[0]):
            for j in range(size[1]):
                if (board[i, j] and clicked[i, j] == 0):
                    # Mine and Unclicked -> Red
                    pygame.draw.rect(surface=screen, color=mine_color, rect=(square_size * i, square_size * j, square_size, square_size))
                elif (board[i, j] and clicked[i, j] == 2):
                    # Mine and Marked -> Blue
                    pygame.draw.rect(surface=screen, color=marked_color, rect=(square_size * i, square_size * j, square_size, square_size))
                elif (not board[i, j] and clicked[i, j] == 2):
                    # Not and Mine and Marked -> Black
                    pygame.draw.rect(surface=screen, color=(0, 0, 0), rect=(square_size * i, square_size * j, square_size, square_size))
    
    elif ai_enabled:
        marks = mark_adjacent_ai(board, clicked, adjacent)
        #marks = np.zeros(shape=board.shape)
        #smartmarks = smart_ai_mode(board, clicked, adjacent)
        smartmarks = np.zeros(shape=board.shape)
        #print(marks)
        for i in range(size[0]):
            for j in range(size[1]):
                if marks[i, j] == 1 or smartmarks[i, j] == 1:
                    # Means it is a safe square
                    if ai_moves:
                        ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=((i + .5)*square_size, (j + .5)*square_size), button=1)
                        pygame.event.post(ev)
                    else:
                        pygame.draw.rect(surface=screen, color=safe_color, rect=(square_size * i, square_size * j, square_size, square_size))
                elif (marks[i, j] == 2 or smartmarks[i, j] == 2):
                    if ai_moves:
                        ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=((i + .5)*square_size, (j + .5)*square_size), button=3)
                        pygame.event.post(ev)
                    else:
                        pygame.draw.rect(surface=screen, color=unsafe_color, rect=(square_size * i, square_size * j, square_size, square_size))
    
                

    # Drawing the Lines
    for i in range(size[0]):
        pygame.draw.rect(surface=screen, color=(120, 120, 120), rect=(i * square_size - 1, 0, 2, size[1] * square_size))
    for j in range(size[1]):
        pygame.draw.rect(surface=screen, color=(120, 120, 120), rect=(0, j * square_size - 1, size[0] * square_size, 2))

    # Draws the Reset button
    pygame.draw.rect(surface=screen, color=(50, 50, 160), rect=((size[0] * square_size - restart_size[0]) / 2, size[1] * square_size, restart_size[0], restart_size[1]))
    restart_text = restart_font.render(restart_msg, True, 'White')
    screen.blit(restart_text, dest=((size[0] * square_size - restart_size[0]) / 2 + 33, size[1] * square_size + 9))

    # Desplayes the Mine Counter
    mine_text = restart_font.render(str(curr_mines), True, 'White')
    screen.blit(mine_text, dest=((9, size[1] * square_size + 9)))

    if curr_mines == 0:
        won_game = True
        for i in range(size[0]):
            for j in range(size[1]):
                if board[i, j] == 1 and clicked[i, j] != 2:
                    won_game = False
    if won_game:
        restart_msg = "Good Job, Bro"

    pygame.display.flip()

pygame.quit()