import pygame
from fusional_vergence_game import FusionalVergenceGame
from src.game_type import GameType


BACKGROUND_COLOR = (0, 0, 0)  # black

MENU_ITEMS = ["Base-IN", "Base-OUT", "Exit"]
MENU_ITEMS_SPACING = 60

MENU_ITEM_SELECTED_COLOR = (255, 255, 0)
MENU_ITEM_UNSELECTED_COLOR = (255, 255, 255)
MENU_ITEM_FONT_SIZE = 48

MENU_Y = 200

MENU_FPS = 30

class GameManager:
    def __init__(self, cfg):
        self.cfg = cfg

        pygame.init()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, MENU_ITEM_FONT_SIZE)

        self.running = True
        self.game = None

    def show_menu(self):
        selected = 0

        while True:
            self.screen.fill(BACKGROUND_COLOR)
            for i, option in enumerate(MENU_ITEMS):
                color = MENU_ITEM_SELECTED_COLOR if i == selected else MENU_ITEM_UNSELECTED_COLOR
                text = self.font.render(option, True, color)
                rect = text.get_rect(center=(self.screen.get_width() // 2, MENU_Y + i * MENU_ITEMS_SPACING))
                self.screen.blit(text, rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(MENU_ITEMS)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(MENU_ITEMS)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:
                            return GameType.BASE_IN
                        elif selected == 1:
                            return GameType.BASE_OUT
                        elif selected == 2:
                            return GameType.EXIT
            self.clock.tick(MENU_FPS)

    def start_game(self, game_type):
        self.game = FusionalVergenceGame(self.cfg, game_type)
        self.game.run()

    def run(self):
        while self.running:
            game_type = self.show_menu()
            if game_type == GameType.EXIT:
                pygame.quit()
            else:
                self.start_game(game_type)

