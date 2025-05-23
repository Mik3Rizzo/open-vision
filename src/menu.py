import pygame

from game_type import GameType


BACKGROUND_COLOR = (15, 26, 33)

MENU_ITEMS_DICT = {
    GameType.BASE_IN: "Base IN",
    GameType.BASE_OUT: "Base OUT",
    GameType.JUMP_DUCTION: "Jump Duction",
    GameType.EXIT: "Exit"
}

MENU_ITEMS_SPACING = 60

MENU_ITEM_SELECTED_COLOR = (255, 255, 0)
MENU_ITEM_UNSELECTED_COLOR = (255, 255, 255)
MENU_ITEM_FONT_SIZE = 48

MENU_Y = 200

MENU_FPS = 30

class Menu:
    def __init__(self, cfg, screen):
        self.cfg = cfg
        self.screen = screen

        self.font = pygame.font.SysFont(None, MENU_ITEM_FONT_SIZE)
        self.clock = pygame.time.Clock()

    def show(self):
        keys = list(MENU_ITEMS_DICT.keys())
        selected_game = keys[0]
        while True:
            # Handle events first
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return GameType.EXIT
                if event.type == pygame.KEYDOWN:
                    index = keys.index(selected_game)
                    if event.key == pygame.K_UP:
                        selected_game = keys[(index - 1) % len(keys)]
                    elif event.key == pygame.K_DOWN:
                        selected_game = keys[(index + 1) % len(keys)]
                    elif event.key == pygame.K_RETURN:
                        return selected_game

            # Only draw if the window is still open
            self.screen.fill(BACKGROUND_COLOR)
            for index, (game_type, option) in enumerate(MENU_ITEMS_DICT.items()):
                color = MENU_ITEM_SELECTED_COLOR if game_type == selected_game else MENU_ITEM_UNSELECTED_COLOR
                text = self.font.render(option, True, color)
                rect = text.get_rect(center=(self.screen.get_width() // 2, MENU_Y + index * MENU_ITEMS_SPACING))
                self.screen.blit(text, rect)

            pygame.display.flip()
            self.clock.tick(MENU_FPS)
