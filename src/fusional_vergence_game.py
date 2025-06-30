import pygame
import random
from utils import calc_disparity
from strings import Strings
from game_type import GameType
from prism import Prism
from layer import Layer, LayerType

BACKGROUND_COLOR = (0, 0, 0)  # black

CURSOR_RADIUS = 8
CURSOR_RED_COLOR = (255, 0, 0, 128)
CURSOR_BLUE_COLOR = (0, 0, 255, 128)

TEXT_COLOR = (255, 255, 255)
TEXT_CORRECT_COLOR = (0, 255, 0)  # green
TEXT_WRONG_COLOR = (255, 255, 0)  # yellow

GAME_FPS = 60

class FusionalVergenceGame:

    def __init__(self, cfg, screen, game_type):
        self.cfg = cfg
        self.game_type = game_type

        # PyGame objects
        self.font = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 28)
        self.clock = pygame.time.Clock()

        # Screen
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.disparity = calc_disparity(self.cfg, self.screen_width, self.screen_height)

        # Layer position
        self.layer_x = (self.screen_width - self.cfg.layer_width) // 2
        self.layer_y = (self.screen_height - self.cfg.layer_height) // 2

        # Square position
        self.square_rel_x = random.randint(0, self.cfg.layer_width - self.cfg.square_size)
        self.square_rel_y = random.randint(0, self.cfg.layer_height - self.cfg.square_size)        # Noise matrix, red/blue layers and cursor
        self.noise_matrix = self._create_noise_matrix()
        self.red_layer = Layer(self.cfg, LayerType.RED, self.cfg.layer_width, self.cfg.layer_height, self.cfg.square_size, self.disparity)
        self.blue_layer = Layer(self.cfg, LayerType.BLUE, self.cfg.layer_width, self.cfg.layer_height, self.cfg.square_size, self.disparity)
        self.red_layer_surface = self.red_layer.create_surface(self.noise_matrix, self.square_rel_x, self.square_rel_y)
        self.blue_layer_surface = self.blue_layer.create_surface(self.noise_matrix, self.square_rel_x, self.square_rel_y)
        self.cursor_surface = pygame.Surface((CURSOR_RADIUS * 2, CURSOR_RADIUS * 2), pygame.SRCALPHA)

        # Offsets and scores separated for BASE_IN and BASE_OUT
        self.offset_in = self.cfg.initial_offset
        self.offset_out = self.cfg.initial_offset
        self.score_in = 0
        self.score_out = 0

        # Prism
        if self.game_type == GameType.BASE_IN:
            self.current_prism = Prism.BASE_IN
        elif self.game_type == GameType.BASE_OUT:
            self.current_prism = Prism.BASE_OUT
        else:  # JUMP_DUCTION
            self.current_prism = Prism.BASE_IN

        self.last_result = None

    def _get_current_offset(self):
        # Returns the offset for the current prism type
        return self.offset_in if self.current_prism == Prism.BASE_IN else self.offset_out

    def _set_current_offset(self, value):
        # Sets the offset for the current prism type
        if self.current_prism == Prism.BASE_IN:
            self.offset_in = value
        else:
            self.offset_out = value

    def _increment_score(self):
        if self.current_prism == Prism.BASE_IN:
            self.score_in = self.offset_in
        else:
            self.score_out = self.offset_out

    def _create_noise_matrix(self):
        return [[random.randint(0, self.cfg.noise_intensity) for _ in range(self.cfg.layer_width)] for _ in range(self.cfg.layer_height)]

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Signal to stop running
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # Signal to stop running
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._on_mouse_click()
        return True  # Signal to continue running

    def _on_mouse_click(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_rel_x = mouse_x - self.layer_x
        mouse_rel_y = mouse_y - self.layer_y

        # Check if the click is inside the square
        click_is_on_square = (
            0 <= mouse_rel_x <= self.cfg.layer_width and
            0 <= mouse_rel_y <= self.cfg.layer_height and
            self.square_rel_x <= mouse_rel_x <= self.square_rel_x + self.cfg.square_size and
            self.square_rel_y <= mouse_rel_y <= self.square_rel_y + self.cfg.square_size
        )

        current_offset = self._get_current_offset()
        if click_is_on_square:
            if current_offset < self.cfg.max_offset:
                current_offset += self.cfg.step
            self.last_result = True
            self._increment_score()
        else:
            if current_offset > self.cfg.min_offset:
                current_offset -= self.cfg.step
            self.last_result = False

        self._set_current_offset(current_offset)        
        # Alternate current_prism for JUMP_DUCTION
        if self.game_type == GameType.JUMP_DUCTION:
            self.current_prism = (
                Prism.BASE_IN if self.current_prism == Prism.BASE_OUT else Prism.BASE_OUT
            )

        self.square_rel_x = random.randint(0, self.cfg.layer_width - self.cfg.square_size)
        self.square_rel_y = random.randint(0, self.cfg.layer_height - self.cfg.square_size)

        self.red_layer_surface = self.red_layer.create_surface(self.noise_matrix, self.square_rel_x, self.square_rel_y)
        self.blue_layer_surface = self.blue_layer.create_surface(self.noise_matrix, self.square_rel_x, self.square_rel_y)

    def _draw_scene(self):
        self.screen.fill(BACKGROUND_COLOR)

        # Set offsets based on the current prism type
        if self.current_prism == Prism.BASE_IN:
            red_offset = -self.offset_in
            blue_offset = self.offset_in
        else:
            red_offset = self.offset_out
            blue_offset = -self.offset_out

        self.screen.blit(self.red_layer_surface, (self.layer_x + red_offset, self.layer_y), special_flags=pygame.BLEND_ADD)
        self.screen.blit(self.blue_layer_surface, (self.layer_x + blue_offset, self.layer_y), special_flags=pygame.BLEND_ADD)

        # Draw red and blue cursors
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(self.cursor_surface, CURSOR_RED_COLOR, (CURSOR_RADIUS, CURSOR_RADIUS), CURSOR_RADIUS)
        self.screen.blit(self.cursor_surface, (mouse_x + red_offset - CURSOR_RADIUS, mouse_y - CURSOR_RADIUS), special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(self.cursor_surface, CURSOR_BLUE_COLOR, (CURSOR_RADIUS, CURSOR_RADIUS), CURSOR_RADIUS)
        self.screen.blit(self.cursor_surface, (mouse_x + blue_offset - CURSOR_RADIUS, mouse_y - CURSOR_RADIUS), special_flags=pygame.BLEND_ADD)

        # Draw the score(s)
        score_text = ""
        if self.game_type == GameType.BASE_OUT:
            score_text = Strings.MSG_BASE_OUT_SCORE.format(self.offset_out)
        elif self.game_type == GameType.BASE_IN:
            score_text = Strings.MSG_BASE_IN_SCORE.format(self.offset_in)
        elif self.game_type == GameType.JUMP_DUCTION:
            score_text = Strings.MSG_BASE_IN_SCORE.format(self.offset_in) + " / " + Strings.MSG_BASE_OUT_SCORE.format(self.offset_out)
        score_text_surface = self.font.render(score_text, True, TEXT_COLOR)
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
                self.clock.tick(GAME_FPS)