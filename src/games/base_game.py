import pygame
from strings import Strings
from abc import ABC, abstractmethod


class BaseGame(ABC):

    _BACKGROUND_COLOR = (0, 0, 0)
    _CURSOR_RADIUS = 8
    _CURSOR_RED_COLOR = (255, 0, 0, 128)
    _CURSOR_BLUE_COLOR = (0, 0, 255, 128)
    _TEXT_COLOR = (255, 255, 255)
    _TEXT_CORRECT_COLOR = (0, 255, 0)
    _TEXT_WRONG_COLOR = (255, 255, 0)
    _GAME_FPS = 60

    def __init__(self, cfg, screen):
        if type(self) is BaseGame:
            raise TypeError("BaseGame is an abstract class and cannot be instantiated directly.")
        self.cfg = cfg
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        self.font = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 28)

        self.clock = pygame.time.Clock()
        self.start_ticks = None

        self.cursor_surface = pygame.Surface((self._CURSOR_RADIUS * 2, self._CURSOR_RADIUS * 2), pygame.SRCALPHA)
        self.red_layer_surface = None
        self.blue_layer_surface = None

        self.layer_x = None
        self.layer_y = None
        self.offset = 0

        self.time_left = self.cfg.game_duration_sec
        self.last_correct = None

    def _draw_layers(self):
        """
        Draw the red and blue layers on the screen. 
        """
        # Red layer conventionally goes to the right (right eye), blue layer goes to the left
        self.screen.blit(self.red_layer_surface, (self.layer_x + self.offset, self.layer_y), special_flags=pygame.BLEND_ADD)
        self.screen.blit(self.blue_layer_surface, (self.layer_x - self.offset, self.layer_y), special_flags=pygame.BLEND_ADD)

    def _draw_cursors(self):
        """
        Draw the red and blue cursors.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(self.cursor_surface, self._CURSOR_RED_COLOR, (self._CURSOR_RADIUS, self._CURSOR_RADIUS), self._CURSOR_RADIUS)
        self.screen.blit(self.cursor_surface, (mouse_x + self.offset - self._CURSOR_RADIUS, mouse_y - self._CURSOR_RADIUS), special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(self.cursor_surface, self._CURSOR_BLUE_COLOR, (self._CURSOR_RADIUS, self._CURSOR_RADIUS), self._CURSOR_RADIUS)
        self.screen.blit(self.cursor_surface, (mouse_x - self.offset - self._CURSOR_RADIUS, mouse_y - self._CURSOR_RADIUS), special_flags=pygame.BLEND_ADD)

    def _draw_score(self, score_text):
        """
        Draw the score text at the top left of the screen.
        """
        score_text_surface = self.font.render(score_text, True, self._TEXT_COLOR)
        self.screen.blit(score_text_surface, (20, 20))

    def _draw_timer(self):
        """
        Draw the timer text at the top right of the screen.
        """
        timer_text = Strings.MSG_TIME_LEFT.format(max(0, int(self.time_left)))
        timer_surface = self.font.render(timer_text, True, self._TEXT_COLOR)
        self.screen.blit(timer_surface, (self.screen_width - 190, 20))

    def _draw_last_result(self):
        """
        Draw the last result message (correct or wrong) below the score.
        """
        if self.last_correct is not None:
            result_color = self._TEXT_CORRECT_COLOR if self.last_correct else self._TEXT_WRONG_COLOR
            result_msg = Strings.MSG_CORRECT if self.last_correct else Strings.MSG_WRONG
            result_text_surface = self.font.render(result_msg, True, result_color)
            self.screen.blit(result_text_surface, (20, 60))

    def _draw_quit_message(self):
        """
        Draw the quit message at the bottom center of the screen.
        """
        quit_text_surface = self.font_small.render(Strings.MSG_QUIT, True, self._TEXT_COLOR)
        quit_rect = quit_text_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        self.screen.blit(quit_text_surface, quit_rect)

    def _draw_additional_info(self, additional_info_text):
        """
        Draw an additional game info.
        """
        surface = self.font.render(additional_info_text, True, self._TEXT_COLOR)
        self.screen.blit(surface, (20, 100))
    
    def _draw_scene(self, score_text, additional_info_text=""):
        """
        Draw the full game scene.
        """
        self.screen.fill(self._BACKGROUND_COLOR)
        self._draw_layers()
        self._draw_cursors()
        self._draw_score(score_text)
        self._draw_timer()
        self._draw_last_result()
        self._draw_quit_message()
        self._draw_additional_info(additional_info_text)
        pygame.display.flip()    

    @abstractmethod
    def _on_mouse_click(self):
        """
        Handle mouse click event. 
        Must be implemented by subclasses.
        """
        pass

    def _handle_input(self):
        """
        Handle the input events (quit, escape, mouse click).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._on_mouse_click()
        return True

    def _update_timer(self):
        """
        Update the game timer.

        :return: True iff time remains.
        :rtype: bool
        """
        elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000
        self.time_left = self.cfg.game_duration_sec - elapsed
        return self.time_left > 0

    def run(self, title):
        """
        Run the main game loop.

        :param title: title of the game window
        :type title: str
        """
        pygame.display.set_caption(title)
        pygame.mouse.set_visible(False)
        running = True
        self.start_ticks = pygame.time.get_ticks()
        while running:
            if not self._update_timer():
                break
            running = self._handle_input()
            if running:
                self._draw_scene()
                self.clock.tick(self._GAME_FPS)
