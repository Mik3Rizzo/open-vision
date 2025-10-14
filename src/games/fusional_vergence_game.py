import pygame
import random
from utils import calc_disparity
from strings import Strings
from entities.prism import Prism
from entities.layer import Layer
from enums.game_type import GameType
from enums.layer_type import LayerType
from enums.prism_type import PrismType
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
        
        self.prism_dict = {
            PrismType.BASE_IN: Prism(PrismType.BASE_IN, self.cfg.initial_offset),
            PrismType.BASE_OUT: Prism(PrismType.BASE_OUT, self.cfg.initial_offset)
        }

        if self.game_type == GameType.BASE_IN:
            self.current_prism_type = PrismType.BASE_IN
        elif self.game_type == GameType.BASE_OUT:
            self.current_prism_type = PrismType.BASE_OUT
        else:
            self.current_prism_type = PrismType.BASE_IN

    def _get_score_msg(self):
        if self.game_type == GameType.BASE_OUT:
            return Strings.MSG_BASE_OUT_SCORE.format(self.prism_dict[PrismType.BASE_OUT].offset)
        elif self.game_type == GameType.BASE_IN:
            return Strings.MSG_BASE_IN_SCORE.format(self.prism_dict[PrismType.BASE_IN].offset)
        elif self.game_type == GameType.JUMP_DUCTION:
            return Strings.MSG_BASE_IN_SCORE.format(self.prism_dict[PrismType.BASE_IN].offset) + " / " + Strings.MSG_BASE_OUT_SCORE.format(self.prism_dict[PrismType.BASE_OUT].offset)
        else:
            return ""

    def _get_break_recovery_cycles_msg(self):
        parts = []
        for _, prism in self.prism_dict.items():
            if prism.break_recovery_pairs:
                osc_str = ", ".join(f"{min_val}-{max_val}" for min_val, max_val in prism.break_recovery_pairs)
                parts.append(f"{prism.prism_type.value.split('_')[1]} {osc_str}")
        if not parts:
            return ""
        return f"B-R cycles: {' | '.join(parts)}"
        
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

        prism = self.prism_dict[self.current_prism_type]
        if click_is_on_square:
            self.last_correct = True
            if not prism.direction:  # Was decreasing, now increasing: save the break-recovery cycle and reset min/max
                prism.break_recovery_pairs.append((prism.current_max, prism.current_min))
                prism.current_min = prism.offset
                prism.current_max = prism.offset
            prism.direction = True
            # Increase offset and update max
            if prism.offset < self.cfg.max_offset:
                prism.offset += self.cfg.step
                prism.current_max = prism.offset
        else:
            self.last_correct = False
            prism.direction = False
            # Decrease offset and update min
            if prism.offset > self.cfg.min_offset:
                prism.offset -= self.cfg.step
                prism.current_min = prism.offset

        # Alternate current_prism for JUMP_DUCTION
        if self.game_type == GameType.JUMP_DUCTION:
            self.current_prism_type = (
                PrismType.BASE_IN if self.current_prism_type == PrismType.BASE_OUT else PrismType.BASE_OUT
            )

        self.square_rel_x = random.randint(0, self.cfg.layer_width - self.cfg.square_size)
        self.square_rel_y = random.randint(0, self.cfg.layer_height - self.cfg.square_size)

        self.red_layer_surface = self.red_layer.create_surface(self.noise_matrix, self.square_rel_x, self.square_rel_y)
        self.blue_layer_surface = self.blue_layer.create_surface(self.noise_matrix, self.square_rel_x, self.square_rel_y)

    def _draw_scene(self):
        if self.current_prism_type == PrismType.BASE_IN:
            self.offset = -self.prism_dict[PrismType.BASE_IN].offset
        else:
            self.offset = self.prism_dict[PrismType.BASE_OUT].offset

        super()._draw_scene(
            score_text=self._get_score_msg(),
            additional_info_text=self._get_break_recovery_cycles_msg()
        )

    def run(self):
        super().run(title=Strings.FUSIONAL_VERGENCE_TITLE)
        # Close the last break-recovery cycle if needed
        for prism in self.prism_dict.values():
            if prism.direction and (not prism.break_recovery_pairs or prism.break_recovery_pairs[-1][0] != prism.offset):
                prism.break_recovery_pairs.append((prism.offset, prism.current_min))
