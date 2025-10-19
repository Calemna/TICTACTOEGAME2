import pygame
import sys

# === Initialization ===
pygame.init()
screen = pygame.display.set_mode((800, 700))
pygame.display.set_caption("TIC TAC TOE")

# === Fonts and Titles ===
font_title = pygame.font.Font('pixel-operator-mono-bold.ttf', 130)
font_mode = pygame.font.Font('pixel-operator-mono-bold.ttf', 100)
font_result = pygame.font.Font(None, 80)
title_text = font_title.render('TIC TAC TOE', False, (0, 0, 0))
mode_text = font_mode.render('MODE SELECTION', False, (255, 0, 0))

# === Assets ===
icon_image = pygame.image.load('captionimage.png')
pygame.display.set_icon(icon_image)
background = pygame.transform.scale(pygame.image.load('backgroundimage.png'), (800, 700))

x_image = pygame.image.load('x_image.png')
o_image = pygame.image.load('o_image.png')
x_image = pygame.transform.scale(x_image, (120, 120))
o_image = pygame.transform.scale(o_image, (120, 120))
back_image = pygame.image.load('back_image.png')
back_image = pygame.transform.scale(back_image, (120, 120))

menu_image = pygame.image.load('menu_button.png')
menu_image = pygame.transform.scale(menu_image, (120, 120))
resultboard_image = pygame.image.load('result_board.png')
resultboard_image = pygame.transform.scale(resultboard_image, (250, 300))
continue_image = pygame.image.load('continue_button.png')
continue_image = pygame.transform.scale(continue_image, (140, 120))

# === Buttons ===
button_clicked = pygame.transform.scale(pygame.image.load('Playclicked.png'), (200, 100))
button_unclicked = pygame.transform.scale(pygame.image.load('Playunclick.png'), (200, 100))
button_rect = button_unclicked.get_rect(center=(400, 400))
button_pvp = pygame.transform.scale(pygame.image.load('Player vs player button.png'), (200, 100))
button_ai = pygame.transform.scale(pygame.image.load('Player vs AI button.png'), (200, 100))
button_pvp_rect = button_pvp.get_rect(center=(400, 300))
button_ai_rect = button_ai.get_rect(center=(400, 450))
menu_button_rect = menu_image.get_rect(topleft=(10, 10))
back_image_rect = back_image.get_rect(center= (390, 320))
continue_button_rect = continue_image.get_rect(center=(390, 270))
# === Game State ===
scene = "menu"
clicked = False
to_move = 'X'
board = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
graphical_board = [[[None, None] for _ in range(3)] for _ in range(3)]

# === Functions ===

def draw_grid():
    grid_color = (0, 0, 0)
    cell_size = 235  # Wider columns
    start_x = (800 - cell_size * 3) // 2
    start_y = ((700 - cell_size * 3) // 2) - 5  # Shift rows upward by 20px
    for i in range(1, 3):
        pygame.draw.line(screen, grid_color, (start_x, start_y + i * cell_size), (start_x + cell_size * 3, start_y + i * cell_size), 5)
        pygame.draw.line(screen, grid_color, (start_x + i * cell_size, start_y), (start_x + i * cell_size, start_y + cell_size * 3), 5)


def render_board():
    cell_size = 235  # Match draw_grid
    start_x = (800 - cell_size * 3) // 2
    start_y = ((700 - cell_size * 3) // 2) - 5
    for i in range(3):
        for j in range(3):
            if board[i][j] == 'X':
                graphical_board[i][j][0] = x_image
            elif board[i][j] == 'O':
                graphical_board[i][j][0] = o_image
            if graphical_board[i][j][0]:
                center_x = start_x + j * cell_size + cell_size // 2
                center_y = start_y + i * cell_size + cell_size // 2
                graphical_board[i][j][1] = graphical_board[i][j][0].get_rect(center=(center_x, center_y))
                screen.blit(graphical_board[i][j][0], graphical_board[i][j][1])


def add_XO():
    global to_move
    mouse_x, mouse_y = pygame.mouse.get_pos()
    cell_size = 235  # Match draw_grid
    start_x = (800 - cell_size * 3) // 2
    start_y = ((700 - cell_size * 3) // 2) - 5
    grid_x = (mouse_x - start_x) // cell_size
    grid_y = (mouse_y - start_y) // cell_size
    if 0 <= grid_x < 3 and 0 <= grid_y < 3:
        if board[grid_y][grid_x] not in ['X', 'O']:
            board[grid_y][grid_x] = to_move
            to_move = 'O' if to_move == 'X' else 'X'
            render_board()



def check_winner():
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i]:
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    if all(cell in ['X', 'O'] for row in board for cell in row):
        return 'Draw'
    return None

def reset_board():
    global board, graphical_board, to_move
    board = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    to_move = 'X'



# === Scene Loops ===

def menu_scene():
    global scene, clicked
    while scene == "menu":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    clicked = True
                    scene = "game"
            elif event.type == pygame.MOUSEBUTTONUP:
                if button_rect.collidepoint(event.pos) and clicked:
                    clicked = False
        screen.blit(background, (0, 0))
        screen.blit(title_text, (40, 70))
        screen.blit(button_clicked if clicked else button_unclicked, button_rect)
        pygame.display.update()

def game_scene():
    global scene, clicked
    while scene == "game":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_pvp_rect.collidepoint(event.pos):
                    clicked = True
                    scene = "playervsplayer"
                elif button_ai_rect.collidepoint(event.pos):
                    clicked = True
                    scene = "playervsai"
        screen.blit(background, (0, 0))
        screen.blit(button_pvp, button_pvp_rect)
        screen.blit(button_ai, button_ai_rect)
        screen.blit(mode_text, (50, 70))
        pygame.display.update()

def playervsplayer_scene():
    global board, to_move, scene
    winner = None
    menu_board = False
    restart = False
    while scene == "playervsplayer":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button_rect.collidepoint(event.pos):
                    clicked = True
                    menu_board = True
                    reset_board()
                elif not winner:
                    add_XO()
                    winner = check_winner()
                
        screen.blit(background, (0, 0))
        screen.blit(menu_image, menu_button_rect)
        draw_grid()
        render_board()
        if menu_board:
            screen.blit(resultboard_image, (260, 190))
            screen.blit(back_image, back_image_rect)
            screen.blit(continue_image, continue_button_rect)
        if winner:
            message = f"{winner} wins!" if winner != 'Draw' else "It's a draw!"
            result_font = pygame.font.Font('pixel-operator-mono-bold.ttf', 30)
            result_text = result_font.render(message, True, (255, 0, 0))
            screen.blit(resultboard_image, (260, 190))
            screen.blit(result_text, (333, 300))
            pygame.display.update()
            pygame.time.delay(2000)
            reset_board()
            
        pygame.display.update()

def playervsai_scene():
    while scene == "playervsai":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.blit(background, (0, 0))
        pygame.display.update()

# === Main Loop ===

while True:
    if scene == "menu":
        menu_scene()
    elif scene == "game":
        game_scene()
    elif scene == "playervsplayer":
        playervsplayer_scene()
    elif scene == "playervsai":
        playervsai_scene()
