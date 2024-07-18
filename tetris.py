import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 6 * BLOCK_SIZE
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

COLORS = [CYAN, YELLOW, MAGENTA, RED, GREEN, BLUE, ORANGE]

class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = Tetromino()
        self.game_over = False
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.game_started = False
        self.fall_speed = 1.0  # Initial fall speed: 1 second
        self.last_fall_time = time.time()
        self.level = 1

    def draw_grid(self):
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                pygame.draw.rect(self.screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(self.screen, GRAY, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_piece(self, piece, offset_x=0, offset_y=0):
        if piece:
            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, piece.color,
                                         ((piece.x + x + offset_x) * BLOCK_SIZE,
                                          (piece.y + y + offset_y) * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE), 0)
                        pygame.draw.rect(self.screen, GRAY,
                                         ((piece.x + x + offset_x) * BLOCK_SIZE,
                                          (piece.y + y + offset_y) * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_next_piece(self):
        next_piece_text = self.small_font.render("Next Piece:", True, WHITE)
        self.screen.blit(next_piece_text, (GRID_WIDTH * BLOCK_SIZE + 10, BLOCK_SIZE))
        
        preview_offset_x = GRID_WIDTH + 1
        preview_offset_y = 3
        
        for y, row in enumerate(self.next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.next_piece.color,
                                     ((preview_offset_x + x) * BLOCK_SIZE,
                                      (preview_offset_y + y) * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 0)
                    pygame.draw.rect(self.screen, GRAY,
                                     ((preview_offset_x + x) * BLOCK_SIZE,
                                      (preview_offset_y + y) * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_sidebar(self):
        sidebar_x = GRID_WIDTH * BLOCK_SIZE
        pygame.draw.rect(self.screen, BLACK, (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, WHITE, (sidebar_x, 0), (sidebar_x, SCREEN_HEIGHT))

        self.draw_next_piece()

        score_text = self.font.render(f"Score:", True, WHITE)
        score_value = self.font.render(f"{self.score}", True, WHITE)
        level_text = self.font.render(f"Level:", True, WHITE)
        level_value = self.font.render(f"{self.level}", True, WHITE)

        self.screen.blit(score_text, (sidebar_x + 10, SCREEN_HEIGHT // 2))
        self.screen.blit(score_value, (sidebar_x + 10, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(level_text, (sidebar_x + 10, SCREEN_HEIGHT // 2 + 90))
        self.screen.blit(level_value, (sidebar_x + 10, SCREEN_HEIGHT // 2 + 130))

    def collide(self, piece, dx=0, dy=0):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if (piece.x + x + dx < 0 or
                        piece.x + x + dx >= GRID_WIDTH or
                        piece.y + y + dy >= GRID_HEIGHT or
                        self.grid[piece.y + y + dy][piece.x + x + dx] != BLACK):
                        return True
        return False

    def merge_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()
        if self.collide(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        full_lines = [i for i, row in enumerate(self.grid) if all(cell != BLACK for cell in row)]
        for line in full_lines:
            del self.grid[line]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        self.score += len(full_lines) ** 2 * 100
        self.update_level()

    def update_level(self):
        self.level = self.score // 1000 + 1
        self.fall_speed = max(0.5, 1.0 - (self.level - 1) * 0.05)  # Speed up gradually, min 0.5 seconds

    def draw_button(self, text, position, size):
        button_rect = pygame.Rect(position, size)
        pygame.draw.rect(self.screen, GREEN, button_rect)
        button_text = self.font.render(text, True, BLACK)
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)
        return button_rect

    def draw_start_screen(self):
        self.screen.fill(BLACK)
        title_text = self.font.render("Tetris", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))
        return self.draw_button("Start", (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 25), (100, 50))

    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("Game Over", True, WHITE)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 4 + 50))

        retry_button = self.draw_button("Retry", (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50), (100, 50))
        exit_button = self.draw_button("Exit", (SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 50), (100, 50))

        return retry_button, exit_button

    def drop_piece(self):
        while not self.collide(self.current_piece, dy=1):
            self.current_piece.y += 1
        self.merge_piece()
        self.last_fall_time = time.time()

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            
            if not self.game_started:
                start_button = self.draw_start_screen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if start_button.collidepoint(event.pos):
                            self.game_started = True
                            self.current_piece = Tetromino()
                            self.last_fall_time = time.time()
            elif self.game_over:
                retry_button, exit_button = self.draw_game_over_screen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if retry_button.collidepoint(event.pos):
                            self.reset_game()
                            self.game_started = True
                            self.current_piece = Tetromino()
                            self.last_fall_time = time.time()
                        elif exit_button.collidepoint(event.pos):
                            running = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT and not self.collide(self.current_piece, dx=-1):
                            self.current_piece.x -= 1
                        if event.key == pygame.K_RIGHT and not self.collide(self.current_piece, dx=1):
                            self.current_piece.x += 1
                        if event.key == pygame.K_DOWN and not self.collide(self.current_piece, dy=1):
                            self.current_piece.y += 1
                            self.last_fall_time = time.time()  # Reset fall time when manually moving down
                        if event.key == pygame.K_SPACE:
                            self.current_piece.rotate()
                            if self.collide(self.current_piece):
                                self.current_piece.rotate()
                                self.current_piece.rotate()
                                self.current_piece.rotate()
                        if event.key == pygame.K_RETURN:
                            self.drop_piece()

                current_time = time.time()
                if current_time - self.last_fall_time > self.fall_speed:
                    if not self.collide(self.current_piece, dy=1):
                        self.current_piece.y += 1
                    else:
                        self.merge_piece()
                    self.last_fall_time = current_time

                self.screen.fill(BLACK)
                self.draw_grid()
                self.draw_piece(self.current_piece)
                self.draw_sidebar()

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
    
#___________python tetris.py