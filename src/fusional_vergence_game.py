import pygame
import random
from utils import calc_disparity

COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)

class FusionalVergenceGame:

    def __init__(self, cfg):
        self.cfg = cfg

        pygame.init()
        
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        
        self.clock = pygame.time.Clock()

        self.min_offset = self.cfg.min_offset
        self.max_offset = self.cfg.max_offset
        self.offset = self.cfg.initial_offset
        self.step = self.cfg.step
        
        self.disparity = calc_disparity(self.cfg, self.screen_width, self.screen_height)
        
        self.cursor_radius = 8

        self.layer_x = (self.screen_width - self.cfg.layer_width) // 2
        self.layer_y = (self.screen_height - self.cfg.layer_height) // 2

        self.square_pos = (
            random.randint(0, self.cfg.layer_width - self.cfg.square_size),
            random.randint(0, self.cfg.layer_height - self.cfg.square_size)
        )

        self.noise_matrix = self._create_noise_matrix()
        self.red_layer = self._create_layer(COLOR_RED, self.square_pos)
        self.blue_layer = self._create_layer(COLOR_BLUE, self.square_pos)
        
        self.font = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 28)

        self.last_result = None


    def _create_noise_matrix(self):
        return [[random.randint(0, self.cfg.noise_intensity) for _ in range(self.cfg.layer_width)] for _ in range(self.cfg.layer_height)]

    def _create_layer(self, color, square_pos):
        surf = pygame.Surface((self.cfg.layer_width, self.cfg.layer_height))
        for y in range(self.cfg.layer_height):
            for x in range(self.cfg.layer_width):
                val = self.noise_matrix[y][x]
                
                if color == COLOR_RED:
                    inside_square = (
                        square_pos[0] <= x < square_pos[0] + self.cfg.square_size and
                        square_pos[1] <= y < square_pos[1] + self.cfg.square_size
                    )
                elif color == COLOR_BLUE:
                    inside_square = (
                        square_pos[0] + self.disparity <= x < square_pos[0] + self.cfg.square_size + self.disparity and
                        square_pos[1] <= y < square_pos[1] + self.cfg.square_size
                    )
                else:
                    inside_square = False

                if inside_square:
                    if color == COLOR_RED:
                        val = self.noise_matrix[y][x]
                    elif color == COLOR_BLUE:
                        src_x = x - self.disparity
                        if 0 <= src_x < self.cfg.layer_width:
                            val = self.noise_matrix[y][src_x]
                if color == COLOR_RED:
                    surf.set_at((x, y), (val, 0, 0))
                elif color == COLOR_BLUE:
                    surf.set_at((x, y), (0, 0, val))
        return surf



    def run(self):
        
        pygame.display.set_caption("Verge Fusion Game")

        running = True
        
        while running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            rel_x = mouse_x - (self.layer_x + self.cfg.layer_width // 2)
            rel_y = mouse_y - (self.layer_y + self.cfg.layer_height // 2)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cursor_red_x = self.cfg.layer_width // 2 + rel_x
                    cursor_red_y = self.cfg.layer_height // 2 + rel_y

                    if (0 <= cursor_red_x < self.cfg.layer_width and 0 <= cursor_red_y < self.cfg.layer_height and
                        self.square_pos[0] <= cursor_red_x < self.square_pos[0] + self.cfg.square_size and
                        self.square_pos[1] <= cursor_red_y < self.square_pos[1] + self.cfg.square_size):
                        if self.offset < self.max_offset:
                            self.offset += self.step
                        self.last_result = True
                    else:
                        if self.offset > self.min_offset:
                            self.offset -= self.step
                        self.last_result = False

                    self.square_pos = (
                        random.randint(0, self.cfg.layer_width - self.cfg.square_size),
                        random.randint(0, self.cfg.layer_height - self.cfg.square_size)
                    )

                    self.red_layer = self._create_layer(COLOR_RED, self.square_pos)
                    self.blue_layer = self._create_layer(COLOR_BLUE, self.square_pos)

            cursor_red_screen_x = self.layer_x - self.offset + self.cfg.layer_width // 2 + rel_x
            cursor_red_screen_y = self.layer_y + self.cfg.layer_height // 2 + rel_y
            cursor_blue_screen_x = self.layer_x + self.offset + self.cfg.layer_width // 2 + rel_x
            cursor_blue_screen_y = self.layer_y + self.cfg.layer_height // 2 + rel_y

            self.screen.fill(COLOR_BLACK)
            self.screen.blit(self.red_layer, (self.layer_x - self.offset, self.layer_y), special_flags=pygame.BLEND_ADD)
            self.screen.blit(self.blue_layer, (self.layer_x + self.offset, self.layer_y), special_flags=pygame.BLEND_ADD)

            cursor_surface = pygame.Surface((self.cursor_radius*2, self.cursor_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(cursor_surface, (255, 0, 0, 180), (self.cursor_radius, self.cursor_radius), self.cursor_radius)
            self.screen.blit(cursor_surface, (cursor_red_screen_x - self.cursor_radius, cursor_red_screen_y - self.cursor_radius))
            cursor_surface = pygame.Surface((self.cursor_radius*2, self.cursor_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(cursor_surface, (0, 0, 255, 180), (self.cursor_radius, self.cursor_radius), self.cursor_radius)
            self.screen.blit(cursor_surface, (cursor_blue_screen_x - self.cursor_radius, cursor_blue_screen_y - self.cursor_radius))

            score_text = self.font.render(f"Score: {self.offset}", True, (255, 255, 255))
            self.screen.blit(score_text, (20, 20))
            if self.last_result is not None:
                if self.last_result:
                    result_text = self.font.render("Correct! (+)", True, (0, 255, 0))
                else:
                    result_text = self.font.render("Wrong! (-)", True, (255, 255, 0))
                self.screen.blit(result_text, (20, 60))

            quit_text = self.font_small.render("Press ESC to quit", True, (255, 255, 255))
            quit_rect = quit_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 40))
            self.screen.blit(quit_text, quit_rect)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()