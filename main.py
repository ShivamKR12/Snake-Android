# main.py

"""
IMPROVEMENTS TO BE MADE: 

1. [FIXED] Don't process inputs faster than the movement of the snake, since that would cause the snake to collide with itself, at the very start of the game, if done fast enough ! (which shouldn't be technically possible)
"""

import pygame, sys, random
from pygame.math import Vector2
import os

# Define fixed virtual constants
CELL_SIZE = 30 
CELL_NUMBER = 20 
FRAMERATE = 60 

# Virtual dimensions the game logic thinks it has
VIRTUAL_WIDTH = CELL_NUMBER * CELL_SIZE   # 600
VIRTUAL_HEIGHT = CELL_NUMBER * CELL_SIZE  # 600

# Track swipe positions globally
touch_start_pos = None
SWIPE_THRESHOLD = 20  

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class SNAKE:
    def __init__(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0, 0)
        self.new_block = False

        self.head_up = pygame.image.load(resource_path('Graphics/head_up.png')).convert_alpha()
        self.head_down = pygame.image.load(resource_path('Graphics/head_down.png')).convert_alpha()
        self.head_right = pygame.image.load(resource_path('Graphics/head_right.png')).convert_alpha()
        self.head_left = pygame.image.load(resource_path('Graphics/head_left.png')).convert_alpha()

        self.tail_up = pygame.image.load(resource_path('Graphics/tail_up.png')).convert_alpha()
        self.tail_down = pygame.image.load(resource_path('Graphics/tail_down.png')).convert_alpha()
        self.tail_right = pygame.image.load(resource_path('Graphics/tail_right.png')).convert_alpha()
        self.tail_left = pygame.image.load(resource_path('Graphics/tail_left.png')).convert_alpha()

        self.body_vertical = pygame.image.load(resource_path('Graphics/body_vertical.png')).convert_alpha()
        self.body_horizontal = pygame.image.load(resource_path('Graphics/body_horizontal.png')).convert_alpha()

        self.body_tr = pygame.image.load(resource_path('Graphics/body_tr.png')).convert_alpha()
        self.body_tl = pygame.image.load(resource_path('Graphics/body_tl.png')).convert_alpha()
        self.body_br = pygame.image.load(resource_path('Graphics/body_br.png')).convert_alpha()
        self.body_bl = pygame.image.load(resource_path('Graphics/body_bl.png')).convert_alpha()

        self.crunch_sound = pygame.mixer.Sound(resource_path('Sound/crunch.wav'))
    
    def draw_snake(self, surface):
        self.update_head_graphics()
        self.update_tail_graphics()

        for index, block in enumerate(self.body):
            x_position = int(block.x * CELL_SIZE)
            y_position = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x_position, y_position, CELL_SIZE, CELL_SIZE)
            
            if index == 0:
                surface.blit(self.head, block_rect)
            elif index == len(self.body) - 1:
                surface.blit(self.tail, block_rect)
            else:
                previous_block = self.body[index + 1] - block
                next_block = self.body[index - 1] - block
                if previous_block.x == next_block.x:
                    surface.blit(self.body_vertical, block_rect)
                elif previous_block.y == next_block.y:
                    surface.blit(self.body_horizontal, block_rect)
                else:
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
                        surface.blit(self.body_tl, block_rect)
                    elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
                        surface.blit(self.body_bl, block_rect)
                    # --- FIXED TYPO HERE (Changed next_x to next_block.x) ---
                    elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
                        surface.blit(self.body_tr, block_rect)
                    elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
                        surface.blit(self.body_br, block_rect)
    
    def move_snake(self):
        if self.new_block == True:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
    
    def add_block(self):
        self.new_block = True
    
    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0]
        if head_relation == Vector2(1, 0):
            self.head = self.head_left
        elif head_relation == Vector2(-1, 0):
            self.head = self.head_right
        elif head_relation == Vector2(0, 1):
            self.head = self.head_up
        elif head_relation == Vector2(0, -1):
            self.head = self.head_down
    
    def update_tail_graphics(self):
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == Vector2(1, 0):
            self.tail = self.tail_left
        elif tail_relation == Vector2(-1, 0):
            self.tail = self.tail_right
        elif tail_relation == Vector2(0, 1):
            self.tail = self.tail_up
        elif tail_relation == Vector2(0, -1):
            self.tail = self.tail_down

    def play_crunch_sound(self):
        self.crunch_sound.play()

    def reset(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0, 0)


class FRUIT:
    def __init__(self):
        self.randomize()
    
    def draw_fruit(self, surface):
        fruit_rect = pygame.Rect(int(self.position.x * CELL_SIZE), int(self.position.y * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        surface.blit(apple, fruit_rect)
    
    def randomize(self):
        self.x = random.randint(0, CELL_NUMBER - 1)
        self.y = random.randint(0, CELL_NUMBER - 1)
        self.position = Vector2(self.x, self.y)


class MAIN:
    def __init__(self):
        self.snake = SNAKE()
        self.fruit = FRUIT()

    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()
    
    def draw_elements(self, surface):
        self.draw_grass(surface)
        self.snake.draw_snake(surface)
        self.fruit.draw_fruit(surface)
        self.draw_score(surface)
    
    def check_collision(self):
        if self.fruit.position == self.snake.body[0]:
            print(f"[COLLISION] Snake ate Fruit at position: {self.fruit.position}")
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()
        
        for block in self.snake.body[1:]:
            if block == self.fruit.position:
                print(f"[COLLISION] Fruit spawned inside Snake body at: {block}. Re-randomizing!")
                self.fruit.randomize()
    
    def check_fail(self):
        if not 0 <= self.snake.body[0].x < CELL_NUMBER or not 0 <= self.snake.body[0].y < CELL_NUMBER:
            print(f"[GAME OVER] Wall Collision! Snake head was at: {self.snake.body[0]}")
            self.game_over()
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                print(f"[GAME OVER] Self Collision! Snake bit itself at: {block}")
                self.game_over()
    
    def game_over(self):
        self.snake.reset()
    
    def draw_grass(self, surface):
        grass_color = (167, 209, 61)
        for row in range(CELL_NUMBER):
            if row % 2 == 0:
                for column in range(CELL_NUMBER):
                    if column % 2 == 0:
                        grass_rect = pygame.Rect(column * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(surface, grass_color, grass_rect)
            else:
                for column in range(CELL_NUMBER):
                    if column % 2 != 0:
                        grass_rect = pygame.Rect(column * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(surface, grass_color, grass_rect)

    def draw_score(self, surface):
        score_text = str(len(self.snake.body) - 3)
        score_surface = game_font.render(score_text, True, (56, 74, 12))
        score_x = int(CELL_SIZE * CELL_NUMBER - 60)
        score_y = int(CELL_SIZE * CELL_NUMBER - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        apple_rect = apple.get_rect(midright=(score_rect.left, score_rect.centery))
        bg_rect = pygame.Rect(apple_rect.left, apple_rect.top, apple_rect.width + score_rect.width + 6, apple_rect.height)
        pygame.draw.rect(surface, (167, 209, 61), bg_rect)
        surface.blit(score_surface, score_rect)
        surface.blit(apple, apple_rect)
        pygame.draw.rect(surface, (56, 74, 12), bg_rect, 2)


# Initialize Pygame
pygame.init()

# Open surface window configuration with RESIZABLE flag enabled
screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.RESIZABLE)

# Capture actual hardware screen size
current_window_width, current_window_height = pygame.display.get_window_size()

virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
scaled_rect = pygame.Rect(0, 0, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

def recalculate_scale(window_w, window_h):
    """Calculates scaling parameters to fit game cleanly into any resolution layout without stretching."""
    global scaled_rect
    
    scale = min(window_w / VIRTUAL_WIDTH, window_h / VIRTUAL_HEIGHT)
    new_w = int(VIRTUAL_WIDTH * scale)
    new_h = int(VIRTUAL_HEIGHT * scale)
    
    new_x = (window_w - new_w) // 2
    new_y = (window_h - new_h) // 2
    
    scaled_rect = pygame.Rect(new_x, new_y, new_w, new_h)

# Recalculate right away for actual Android resolution boundaries
recalculate_scale(current_window_width, current_window_height)

clock = pygame.time.Clock()
apple = pygame.image.load(resource_path('Graphics/apple.png')).convert_alpha()
game_font = pygame.font.Font(resource_path('Font/PoetsenOne-Regular.ttf'), 25)
pygame.display.set_icon(apple)

SCREEN_UPDATE = pygame.USEREVENT 
pygame.time.set_timer(SCREEN_UPDATE, 150)

main_game = MAIN()

# Main Game Loop
input_handled = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_AC_BACK):
            pygame.quit()
            sys.exit() 
            
        if event.type == SCREEN_UPDATE:
            main_game.update()
            input_handled = False

        elif event.type == pygame.VIDEORESIZE:
            current_window_width, current_window_height = event.w, event.h
            screen = pygame.display.set_mode((current_window_width, current_window_height), pygame.RESIZABLE)
            recalculate_scale(current_window_width, current_window_height)
            
        elif event.type == pygame.FINGERDOWN:
            raw_x = event.x * current_window_width
            raw_y = event.y * current_window_height
            touch_start_pos = Vector2(raw_x, raw_y)
            
        elif event.type == pygame.FINGERMOTION and touch_start_pos is not None:
            raw_x = event.x * current_window_width
            raw_y = event.y * current_window_height
            current_pos = Vector2(raw_x, raw_y)
            
            delta = current_pos - touch_start_pos
            
            if delta.length() > SWIPE_THRESHOLD:
                if not input_handled:
                    if abs(delta.x) > abs(delta.y):
                        if delta.x > 0 and main_game.snake.direction.x != -1:
                            main_game.snake.direction = Vector2(1, 0)
                            input_handled = True
                        elif delta.x < 0 and main_game.snake.direction.x != 1:
                            main_game.snake.direction = Vector2(-1, 0)
                            input_handled = True
                    else:
                        if delta.y > 0 and main_game.snake.direction.y != -1:
                            main_game.snake.direction = Vector2(0, 1)
                            input_handled = True
                        elif delta.y < 0 and main_game.snake.direction.y != 1:
                            main_game.snake.direction = Vector2(0, -1)
                            input_handled = True
                
                touch_start_pos = current_pos

        elif event.type == pygame.FINGERUP:
            touch_start_pos = None

    # Clear both display horizons
    screen.fill((40, 40, 40)) 
    virtual_surface.fill((175, 215, 70)) 

    # Render components onto base surface
    main_game.draw_elements(virtual_surface)
    
    # Scale components dynamically using transform pipeline
    scaled_surface = pygame.transform.smoothscale(virtual_surface, (scaled_rect.width, scaled_rect.height))
    
    # Blit cleanly into centered layout coordinates
    screen.blit(scaled_surface, scaled_rect.topleft)

    pygame.display.update()
    clock.tick(FRAMERATE)
