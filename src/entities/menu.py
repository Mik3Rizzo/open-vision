import pygame


BACKGROUND_COLOR = (15, 26, 33)
MENU_Y = 200
MENU_FPS = 30

MENU_ITEM_SELECTED_COLOR = (255, 255, 0)
MENU_ITEM_UNSELECTED_COLOR = (255, 255, 255)
MENU_ITEM_FONT_SIZE = 48
MENU_ITEMS_SPACING = 60


class Menu:
    _EXIT_KEY = "EXIT"
    _EXIT_VALUE = "Exit"

    def __init__(self, cfg, screen, items_enum=[], title=None, subtitle=None):
        self.cfg = cfg
        self.screen = screen

        self.items_dict = {member: member.value for member in items_enum} if items_enum else {}
        # Always add "exit" as the last item
        self.items_dict[self._EXIT_KEY] = self._EXIT_VALUE

        self.title = title
        self.subtitle = subtitle

        self.font = pygame.font.SysFont(None, MENU_ITEM_FONT_SIZE)
        self.title_font = pygame.font.SysFont(None, 48)
        self.subtitle_font = pygame.font.SysFont(None, 36)
        self.clock = pygame.time.Clock()

    def show(self):
        keys = list(self.items_dict.keys())
        selected_item = keys[0]
        while True:
            # Handle events first
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    index = keys.index(selected_item)
                    if event.key == pygame.K_UP:
                        selected_item = keys[(index - 1) % len(keys)]
                    elif event.key == pygame.K_DOWN:
                        selected_item = keys[(index + 1) % len(keys)]
                    elif event.key == pygame.K_RETURN:
                        if selected_item == self._EXIT_KEY:
                            return None
                        return selected_item

            # Only draw if the window is still open
            self.screen.fill(BACKGROUND_COLOR)
            
            y_offset = 100
            if self.title:
                title_text = self.title_font.render(self.title, True, (255, 255, 255))
                title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
                self.screen.blit(title_text, title_rect)
                y_offset += 60
            
            if self.subtitle:
                subtitle_text = self.subtitle_font.render(self.subtitle, True, (255, 255, 255))
                subtitle_rect = subtitle_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
                self.screen.blit(subtitle_text, subtitle_rect)
                y_offset += 60
            
            menu_y = y_offset + 40
            for index, (item, option) in enumerate(self.items_dict.items()):
                color = MENU_ITEM_SELECTED_COLOR if item == selected_item else MENU_ITEM_UNSELECTED_COLOR
                text = self.font.render(option, True, color)
                rect = text.get_rect(center=(self.screen.get_width() // 2, menu_y + index * MENU_ITEMS_SPACING))
                self.screen.blit(text, rect)

            pygame.display.flip()
            self.clock.tick(MENU_FPS)
