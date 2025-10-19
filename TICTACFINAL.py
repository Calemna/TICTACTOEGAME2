import pygame
import sys
import random
from time import perf_counter

#config
WIDTH, HEIGHT = 800, 700
FPS = 60

#files
ASSETS = {
    "background": "backgroundimage.png",
    "x": "x_image.png",
    "o": "o_image.png",
    "menu_btn": "menu_button.png",
    "play_pvp": "Player vs player button.png",
    "play_ai": "Player vs AI button.png",
    "continue": "continue_button.png",
    "result_board": "result_board.png",
    "icon": "captionimage.png",
}

# INIT
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TIC TAC TOE")
try:
    pygame.display.set_icon(pygame.image.load(ASSETS["icon"]))
except Exception:
    pass
clock = pygame.time.Clock()

# fonts with fallback
def load_font(path, size):
    try:
        return pygame.font.Font(path, size)
    except Exception:
        return pygame.font.SysFont(None, size)

font_title = load_font('pixel-operator-mono-bold.ttf', 90)
font_sub = load_font('pixel-operator-mono-bold.ttf', 48)
font_small = load_font('pixel-operator-mono-bold.ttf', 30)

# ----------------------------
# ASSET LOADING (scaled)
# ----------------------------
def safe_load(path):
    try:
        return pygame.image.load(path)
    except Exception:
        # placeholder surface if asset missing
        s = pygame.Surface((100, 100))
        s.fill((200, 200, 200))
        return s

background = pygame.transform.scale(safe_load(ASSETS["background"]), (WIDTH, HEIGHT))
x_img = pygame.transform.scale(safe_load(ASSETS["x"]), (120, 120))
o_img = pygame.transform.scale(safe_load(ASSETS["o"]), (120, 120))
menu_btn_img = pygame.transform.scale(safe_load(ASSETS["menu_btn"]), (100, 100))
play_pvp_img = pygame.transform.scale(safe_load(ASSETS["play_pvp"]), (220, 100))
play_ai_img = pygame.transform.scale(safe_load(ASSETS["play_ai"]), (220, 100))
continue_img = pygame.transform.scale(safe_load(ASSETS["continue"]), (140, 120))
result_board_img = pygame.transform.scale(safe_load(ASSETS["result_board"]), (250, 300))

# ----------------------------
# UTILS
# ----------------------------
def draw_text_center(text, font, color, y, surf=screen):
    s = font.render(text, True, color)
    r = s.get_rect(center=(WIDTH // 2, y))
    surf.blit(s, r)
    return r

def fade(scene_from_draw_fn, scene_to_draw_fn, duration=400):
    """
    Fade-out then fade-in between scenes (non-blocking-friendly).
    duration in milliseconds (total). We'll do half for fade out, half for fade in.
    This function processes events so window stays responsive.
    """
    half = duration // 2
    start = perf_counter()
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay = overlay.convert_alpha()
    # Fade out
    t0 = perf_counter()
    while True:
        elapsed = (perf_counter() - t0) * 1000
        alpha = min(255, int((elapsed / half) * 255))
        scene_from_draw_fn()
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        if elapsed >= half:
            break
        clock.tick(FPS)
    # Fade in to new scene
    t1 = perf_counter()
    while True:
        elapsed = (perf_counter() - t1) * 1000
        alpha = max(0, 255 - int((elapsed / half) * 255))
        scene_to_draw_fn()
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        if elapsed >= half:
            break
        clock.tick(FPS)

# ----------------------------
# GAME CLASS
# ----------------------------
class TicTacToeGame:
    def __init__(self):
        self.reset()
        self.scene = "menu"  # menu, mode_select, pvp, ai
        self.menu_rect = menu_btn_img.get_rect(topleft=(10, 10))
        self.pvp_rect = play_pvp_img.get_rect(center=(WIDTH // 2, 300))
        self.ai_rect = play_ai_img.get_rect(center=(WIDTH // 2, 450))
        self.cont_rect = continue_img.get_rect(center=(WIDTH // 2, 380))
        self.result_board_pos = (WIDTH // 2 - result_board_img.get_width() // 2, 190)
        self.cell_size = 235
        self.grid_start_x = (WIDTH - self.cell_size * 3) // 2
        self.grid_start_y = ((HEIGHT - self.cell_size * 3) // 2) - 5
        self.ai_delay_ms = 300  # small delay to look natural

    def reset(self):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.current = 'X'
        self.winner = None
        self.ai_thinking = False
        self.ai_think_start = None

    # draw the static background + grid; return start coords
    def draw_grid(self):
        start_x = self.grid_start_x
        start_y = self.grid_start_y
        for i in range(1, 3):
            pygame.draw.line(screen, (0, 0, 0), (start_x, start_y + i * self.cell_size), (start_x + self.cell_size * 3, start_y + i * self.cell_size), 5)
            pygame.draw.line(screen, (0, 0, 0), (start_x + i * self.cell_size, start_y), (start_x + i * self.cell_size, start_y + self.cell_size * 3), 5)
        return start_x, start_y

    def render_board(self):
        start_x, start_y = self.draw_grid()
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 'X':
                    img = x_img
                elif self.board[i][j] == 'O':
                    img = o_img
                else:
                    continue
                rect = img.get_rect(center=(start_x + j * self.cell_size + self.cell_size // 2,
                                            start_y + i * self.cell_size + self.cell_size // 2))
                screen.blit(img, rect)

    def cell_from_pos(self, pos):
        x, y = pos
        gx = (x - self.grid_start_x) // self.cell_size
        gy = (y - self.grid_start_y) // self.cell_size
        if 0 <= gx < 3 and 0 <= gy < 3:
            return int(gy), int(gx)
        return None

    def check_winner(self):
        b = self.board
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] and b[i][0]:
                return b[i][0]
            if b[0][i] == b[1][i] == b[2][i] and b[0][i]:
                return b[0][i]
        if b[0][0] == b[1][1] == b[2][2] and b[0][0]:
            return b[0][0]
        if b[0][2] == b[1][1] == b[2][0] and b[0][2]:
            return b[0][2]
        if all(all(cell for cell in row) for row in b):
            return "Draw"
        return None

    # Player click used in both PvP and PvAI when it's player's turn
    def player_click(self, pos):
        if self.winner:
            return
        cell = self.cell_from_pos(pos)
        if not cell:
            return
        i, j = cell
        if not self.board[i][j]:
            self.board[i][j] = self.current
            self.winner = self.check_winner()
            if not self.winner:
                self.current = 'O' if self.current == 'X' else 'X'

    # MINIMAX AI (unbeatable)
    def ai_move(self):
        if self.winner:
            return
        best_score = -float('inf')
        best_move = None
        # try all moves
        for i in range(3):
            for j in range(3):
                if not self.board[i][j]:
                    self.board[i][j] = 'O'
                    score = self.minimax(0, False)
                    self.board[i][j] = None
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)
        if best_move:
            i, j = best_move
            self.board[i][j] = 'O'
            self.winner = self.check_winner()
            if not self.winner:
                self.current = 'X'

    def minimax(self, depth, is_maximizing):
        result = self.check_winner()
        if result:
            if result == 'O':
                return 1
            elif result == 'X':
                return -1
            elif result == 'Draw':
                return 0

        if is_maximizing:
            best_score = -float('inf')
            for i in range(3):
                for j in range(3):
                    if not self.board[i][j]:
                        self.board[i][j] = 'O'
                        score = self.minimax(depth + 1, False)
                        self.board[i][j] = None
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(3):
                for j in range(3):
                    if not self.board[i][j]:
                        self.board[i][j] = 'X'
                        score = self.minimax(depth + 1, True)
                        self.board[i][j] = None
                        best_score = min(score, best_score)
            return best_score

    # Scenes drawing functions (used by fade)
    def draw_menu(self):
        screen.blit(background, (0, 0))
        draw_text_center("TIC TAC TOE", font_title, (0, 0, 0), 200)
        draw_text_center("CLICK TO START", font_small, (255, 0, 0), 400)

    def draw_mode_select(self):
        screen.blit(background, (0, 0))
        draw_text_center("SELECT MODE", font_sub, (255, 0, 0), 140)
        screen.blit(play_pvp_img, self.pvp_rect)
        screen.blit(play_ai_img, self.ai_rect)

    def draw_game_base(self):
        screen.blit(background, (0, 0))
        # draw grid and board via render_board
        self.render_board()
        screen.blit(menu_btn_img, self.menu_rect)

    # Scenes (loops)
    def menu_scene(self):
        # quick loop until click -> go to mode_select with fade
        while self.scene == "menu":
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    # fade from menu to mode select
                    fade(self.draw_menu, self.draw_mode_select, duration=350)
                    self.scene = "mode_select"
            self.draw_menu()
            pygame.display.update()
            clock.tick(FPS)

    def mode_select_scene(self):
        hover_color = (255, 100, 100)
        while self.scene == "mode_select":
            mouse = pygame.mouse.get_pos()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if self.pvp_rect.collidepoint(e.pos):
                        fade(self.draw_mode_select, self.draw_game_base, duration=350)
                        self.reset()
                        self.scene = "pvp"
                    elif self.ai_rect.collidepoint(e.pos):
                        fade(self.draw_mode_select, self.draw_game_base, duration=350)
                        self.reset()
                        self.scene = "ai"
            # draw
            self.draw_mode_select()
            # hover outline
            if self.pvp_rect.collidepoint(mouse):
                pygame.draw.rect(screen, hover_color, self.pvp_rect.inflate(6, 6), 4, border_radius=8)
            if self.ai_rect.collidepoint(mouse):
                pygame.draw.rect(screen, hover_color, self.ai_rect.inflate(6, 6), 4, border_radius=8)

            pygame.display.update()
            clock.tick(FPS)

    def pvp_scene(self):
        while self.scene == "pvp":
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if self.menu_rect.collidepoint(e.pos):
                        fade(self.draw_game_base, self.draw_mode_select, duration=350)
                        self.scene = "mode_select"
                    else:
                        self.player_click(e.pos)
                # allow quitting while result screen waiting (handled below)

            # draw
            self.draw_game_base()
            draw_text_center(f"{self.current}'s Turn", font_small, (0, 0, 0), 80)

            # show winner overlay if any
            if self.winner:
                self.show_result_screen()
            pygame.display.update()
            clock.tick(FPS)

    def ai_scene(self):
        while self.scene == "ai":
            now = pygame.time.get_ticks()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if self.menu_rect.collidepoint(e.pos):
                        fade(self.draw_game_base, self.draw_mode_select, duration=350)
                        self.scene = "mode_select"
                    else:
                        if self.current == 'X' and not self.winner:
                            # player move
                            self.player_click(e.pos)
                            # if AI should move next, set thinking start so we can delay a little
                            if self.current == 'O' and not self.winner:
                                self.ai_thinking = True
                                self.ai_think_start = now
                # no else

            # if AI is flagged to think and delay has passed, do the move
            if self.ai_thinking and (pygame.time.get_ticks() - (self.ai_think_start or 0) >= self.ai_delay_ms):
                self.ai_thinking = False
                self.ai_move()

            # draw
            self.draw_game_base()
            draw_text_center(f"{self.current}'s Turn", font_small, (0, 0, 0), 80)

            if self.winner:
                self.show_result_screen()
            pygame.display.update()
            clock.tick(FPS)

    def show_result_screen(self):
        # draw board dimmed
        self.draw_game_base()
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (0, 0))
        # result board and text
        screen.blit(result_board_img, self.result_board_pos)
        msg = f"{self.winner} wins!" if self.winner != "Draw" else "It's a draw!"
        draw_text_center(msg, font_small, (255, 0, 0), 300)
        # draw continue and menu buttons inside result area
        cont_rect = continue_img.get_rect(center=(WIDTH // 2, 380))
        screen.blit(continue_img, cont_rect)
        # also draw a small text button to go back to menu
        menu_text = font_small.render("MENU", True, (0, 0, 0))
        menu_rect = menu_text.get_rect(center=(WIDTH // 2, 440))
        screen.blit(menu_text, menu_rect)

        pygame.display.update()
        # wait for click inside result choices (non-blocking loop that still processes events)
        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if cont_rect.collidepoint(e.pos):
                        # stay in same scene, just reset board
                        self.reset()
                        waiting = False
                    elif menu_rect.collidepoint(e.pos):
                        # go back to mode select with fade
                        fade(self.draw_game_base, self.draw_mode_select, duration=350)
                        self.reset()
                        self.scene = "mode_select"
                        waiting = False
            # keep showing overlay while waiting, so UI doesn't freeze
            clock.tick(FPS)

# ----------------------------
# MAIN
# ----------------------------
game = TicTacToeGame()

def main_loop():
    while True:
        if game.scene == "menu":
            game.menu_scene()
        elif game.scene == "mode_select":
            game.mode_select_scene()
        elif game.scene == "pvp":
            game.pvp_scene()
        elif game.scene == "ai":
            game.ai_scene()
        else:
            game.scene = "menu"  # fallback

if __name__ == "__main__":
    main_loop()
