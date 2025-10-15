import pygame
from games.fusional_vergence_game import FusionalVergenceGame
from entities.menu import Menu
from enums.game_type import GameType
from enums.summary_menu_item import SummaryMenuItem
from strings import Strings


class OpenVision:
    def __init__(self, cfg):
        self.cfg = cfg

        pygame.init()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        self.menu = Menu(self.cfg, self.screen, items_enum=GameType)
        self.game = None

    def start_game(self, game_type):
        self.game = FusionalVergenceGame(self.cfg, self.screen, game_type)
        self.game.run()

        # Game over, show summary and handle choice
        summary_menu = Menu(            
            self.cfg, 
            self.screen, 
            items_enum=SummaryMenuItem, 
            title=Strings.SUMMARY_MENU_TITLE, 
            subtitle=f"{self.game._get_score_msg()}\n{self.game._get_break_recovery_cycles_msg()}"
        )
        choice = summary_menu.show()
        if choice == SummaryMenuItem.RESTART:
            self.start_game(game_type)

    def run(self):
        running = True
        while running:
            game_type = self.menu.show()
            if game_type is None:
                running = False
                pygame.quit()
            else:
                self.start_game(game_type)

