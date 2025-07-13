import pygame
import random
from utils import calc_disparity
from strings import Strings
from entities.prism import Prism
from entities.layer import Layer
from enums.game_type import GameType
from enums.layer_type import LayerType
from games.base_game import BaseGame

class FusionalVergenceGame(BaseGame):

    def __init__(self, cfg, screen, game_type):
        super().__init__(cfg, screen)
        self.game_type = game_type
        self.disparity = calc_disparity(self.cfg, self.screen_width, self.screen_height)

        self.layer_x = (self.screen_width - self.cfg.layer_width) // 2
        self.layer_y = (self.screen_height - self.cfg.layer_height) // 2
        self.square_rel_x = random.randint(0, self.cfg.layer_width - self.cfg.square_size)
        self.square_rel_y = random.randint(0, self.cfg.layer_height - self.cfg.square_size)

        self.noise_matrix = self._create_noise_matrix()
        self.red_layer = Layer(self.cfg, LayerType.RED, self.cfg.layer_width, self.cfg.layer_height, self.cfg.square_size, self.disparity)
        self.blue_layer = Layer(self.cfg, LayerType.BLUE, self.cfg.layer_width, self.cfg.layer_height, self.cfg.square_size, self.disparity)
        self.red_layer_surface = self.red_layer.create_surface(self.noise_matrix, self.square_rel_x, self.square_rel_y)
        self.blue_layer_surface = self.blue_layer.create_surface(self.noise_matrix, self.square_rel_x, self.square_rel_y)
        
        self.offset_in = self.cfg.initial_offset
        self.offset_out = self.cfg.initial_offset

        self.score_in = 0
        self.score_out = 0

        if self.game_type == GameType.BASE_IN:
            self.current_prism = Prism.BASE_IN
        elif self.game_type == GameType.BASE_OUT:
            self.current_prism = Prism.BASE_OUT
        else:
            self.current_prism = Prism.BASE_IN

    def _get_current_offset(self):
        """
        Get the offset for the current prism type.
        """
        return self.offset_in if self.current_prism == Prism.BASE_IN else self.offset_out

    def _set_current_offset(self, value):
        """
        Set the offset for the current prism type.
        """
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
        if self.current_prism == Prism.BASE_IN:
            self.offset = -self.offset_in
        else:
            self.offset = self.offset_out

        if self.game_type == GameType.BASE_OUT:
            score_text = Strings.MSG_BASE_OUT_SCORE.format(self.offset_out)
        elif self.game_type == GameType.BASE_IN:
            score_text = Strings.MSG_BASE_IN_SCORE.format(self.offset_in)
        elif self.game_type == GameType.JUMP_DUCTION:
            score_text = Strings.MSG_BASE_IN_SCORE.format(self.offset_in) + " / " + Strings.MSG_BASE_OUT_SCORE.format(self.offset_out)
        else:
            score_text = ""
        super()._draw_scene(score_text)

    def run(self):
        super().run(title=Strings.FUSIONAL_VERGENCE_TITLE)
