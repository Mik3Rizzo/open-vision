import pygame
import random
from utils import calc_disparity
from strings import Strings 

BACKGROUND_COLOR = (0, 0, 0)  # black
RED_LAYER_COLOR = (255, 0, 0)  
BLUE_LAYER_COLOR = (0, 0, 255)

CURSOR_RADIUS = 8
CURSOR_RED_COLOR = (255, 0, 0, 128)
CURSOR_BLUE_COLOR = (0, 0, 255, 128)

TEXT_COLOR = (255, 255, 255)
TEXT_CORRECT_COLOR = (0, 255, 0)  # green
TEXT_WRONG_COLOR = (255, 255, 0)  # yellow


class FusionalVergenceGame:

    def __init__(self, cfg):
        self.cfg = cfg

        pygame.init()

        self.font = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 28)
        self.clock = pygame.time.Clock()
        
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        self.disparity = calc_disparity(self.cfg, self.screen_width, self.screen_height)

        self.min_offset = self.cfg.min_offset
        self.max_offset = self.cfg.max_offset
        self.offset = self.cfg.initial_offset
        self.step = self.cfg.step

        self.layer_x = (self.screen_width - self.cfg.layer_width) // 2  # Relative to the screen
        self.layer_y = (self.screen_height - self.cfg.layer_height) // 2
        
        self.square_rel_x = random.randint(0, self.cfg.layer_width - self.cfg.square_size)  # Relative to the layer
        self.square_rel_y = random.randint(0, self.cfg.layer_height - self.cfg.square_size)
    
        self.noise_matrix = self._create_noise_matrix()
        self.red_layer_surface = self._create_layer_surface(RED_LAYER_COLOR)
        self.blue_layer_surface = self._create_layer_surface(BLUE_LAYER_COLOR)
        self.cursor_surface = pygame.Surface((CURSOR_RADIUS * 2, CURSOR_RADIUS * 2), pygame.SRCALPHA)

        self.last_result = None

    def _create_noise_matrix(self):
        return [[random.randint(0, self.cfg.noise_intensity) for _ in range(self.cfg.layer_width)] for _ in range(self.cfg.layer_height)]

    def _create_layer_surface(self, color):
        layer_surface = pygame.Surface((self.cfg.layer_width, self.cfg.layer_height))

        for y in range(self.cfg.layer_height):
            for x in range(self.cfg.layer_width):
                val = self.noise_matrix[y][x]

                if color == RED_LAYER_COLOR:
                    xy_is_inside_square = (
                        self.square_rel_x <= x < self.square_rel_x + self.cfg.square_size and
                        self.square_rel_y <= y < self.square_rel_y + self.cfg.square_size
                    )
                elif color == BLUE_LAYER_COLOR:
                    xy_is_inside_square = (
                        self.square_rel_x + self.disparity <= x < self.square_rel_x + self.cfg.square_size + self.disparity and
                        self.square_rel_y <= y < self.square_rel_y + self.cfg.square_size
                    )

                if xy_is_inside_square and color == BLUE_LAYER_COLOR:
                    # For blue square, sample noise from the original (non-disparate) position
                    src_x = x - self.disparity
                    if 0 <= src_x < self.cfg.layer_width:
                        val = self.noise_matrix[y][src_x]
                
                if color == RED_LAYER_COLOR:
                    layer_surface.set_at((x, y), (val, 0, 0))
                elif color == BLUE_LAYER_COLOR:
                    layer_surface.set_at((x, y), (0, 0, val))
        return layer_surface

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Signal to stop running
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # Signal to stop running
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._on_mouse_click()
        return True # Signal to continue running

    def _on_mouse_click(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        mouse_rel_x = mouse_x - self.layer_x
        mouse_rel_y = mouse_y - self.layer_y 

        # Note: the calculation are made using the virtual centered layer and cursor
        click_is_on_square = (
            0 <= mouse_rel_x <= self.cfg.layer_width and
            0 <= mouse_rel_y <= self.cfg.layer_height and
            self.square_rel_x <= mouse_rel_x <= self.square_rel_x + self.cfg.square_size and
            self.square_rel_y <= mouse_rel_y <= self.square_rel_y + self.cfg.square_size
        )

        if click_is_on_square:
            if self.offset < self.max_offset:
                self.offset += self.step
            self.last_result = True
        else:
            if self.offset > self.min_offset:
                self.offset -= self.step
            self.last_result = False

        self.square_rel_x = random.randint(0, self.cfg.layer_width - self.cfg.square_size)
        self.square_rel_y = random.randint(0, self.cfg.layer_height - self.cfg.square_size)

        self.red_layer_surface = self._create_layer_surface(RED_LAYER_COLOR)
        self.blue_layer_surface = self._create_layer_surface(BLUE_LAYER_COLOR)

    def _draw_scene(self):
        self.screen.fill(BACKGROUND_COLOR)

        # Draw red and blue layers
        self.screen.blit(self.red_layer_surface, (self.layer_x - self.offset, self.layer_y), special_flags=pygame.BLEND_ADD)
        self.screen.blit(self.blue_layer_surface, (self.layer_x + self.offset, self.layer_y), special_flags=pygame.BLEND_ADD)

        # Draw red and blue cursors
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(self.cursor_surface, CURSOR_RED_COLOR, (CURSOR_RADIUS, CURSOR_RADIUS), CURSOR_RADIUS)
        self.screen.blit(self.cursor_surface, (mouse_x - self.offset - CURSOR_RADIUS, mouse_y - CURSOR_RADIUS), special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(self.cursor_surface, CURSOR_BLUE_COLOR, (CURSOR_RADIUS, CURSOR_RADIUS), CURSOR_RADIUS)
        self.screen.blit(self.cursor_surface, (mouse_x + self.offset - CURSOR_RADIUS, mouse_y - CURSOR_RADIUS), special_flags=pygame.BLEND_ADD)

        # Draw the score
        score_text_surface = self.font.render(Strings.MSG_SCORE.format(self.offset), True, TEXT_COLOR)
        self.screen.blit(score_text_surface, (20, 20))

        if self.last_result is not None:
            result_color = TEXT_CORRECT_COLOR if self.last_result else TEXT_WRONG_COLOR
            result_msg = Strings.MSG_CORRECT if self.last_result else Strings.MSG_WRONG
            result_text_surface = self.font.render(result_msg, True, result_color)
            self.screen.blit(result_text_surface, (20, 60))

        # Draw quit message
        quit_text_surface = self.font_small.render(Strings.MSG_QUIT, True, TEXT_COLOR)
        quit_rect = quit_text_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        self.screen.blit(quit_text_surface, quit_rect)

        pygame.display.flip()

    def run(self):
        pygame.display.set_caption(Strings.FUSIONAL_VERGENCE_TITLE)
        pygame.mouse.set_visible(False)  # Hide the mouse cursor

        running = True

        while running:
            running = self._handle_input()
            if running:
                self._draw_scene()
                self.clock.tick(60)

        pygame.quit()