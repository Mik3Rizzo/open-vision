import pygame
from src.games.fusional_vergence_game import FusionalVergenceGame
from entities.menu import Menu
from enums.game_type import GameType


class OpenVision:
    def __init__(self, cfg):
        self.cfg = cfg

        pygame.init()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        self.menu = Menu(self.cfg, self.screen)
        self.game = None

    def start_game(self, game_type):
        self.game = FusionalVergenceGame(self.cfg, self.screen, game_type)
        self.game.run()

    def run(self):
        running = True
        while running:
            game_type = self.menu.show()
            if game_type == GameType.EXIT:
                running = False
                pygame.quit()
            else:
                self.start_game(game_type)

