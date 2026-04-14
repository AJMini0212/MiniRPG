import pygame
from data.save_system import has_save

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (40, 40, 40)
YELLOW = (255, 220, 0)
GRAY = (180, 180, 180)


def draw_text(screen, text, x, y, size=24, color=WHITE):
    font = pygame.font.SysFont("malgungothic", size)
    screen.blit(font.render(text, True, color), (x, y))


class MenuScene:
    def __init__(self, screen):
        self.screen = screen
        self.selected = 0
        self.menu_items = ["새 게임"]
        if has_save():
            self.menu_items.insert(1, "계속하기")
        self.menu_items.append("종료")
        self.choice = None

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.menu_items)
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.menu_items)
        elif event.key in (pygame.K_RETURN, pygame.K_z):
            selected_item = self.menu_items[self.selected]
            if selected_item == "새 게임":
                self.choice = "new_game"
            elif selected_item == "계속하기":
                self.choice = "load_game"
            elif selected_item == "종료":
                self.choice = "quit"

    def draw(self):
        self.screen.fill((20, 20, 50))

        # 제목
        draw_text(self.screen, "Mini RPG", 300, 80, 56, YELLOW)

        # 메뉴 아이템
        for i, item in enumerate(self.menu_items):
            y = 200 + i * 70
            color = YELLOW if i == self.selected else WHITE
            bg = (60, 60, 90) if i == self.selected else DARK
            pygame.draw.rect(self.screen, bg, (250, y, 300, 60))
            pygame.draw.rect(self.screen, color, (250, y, 300, 60), 2)

            prefix = "▶ " if i == self.selected else "  "
            draw_text(self.screen, prefix + item, 270, y + 15, 32, color)

        # 조작 안내
        draw_text(self.screen, "위/아래: 선택  Z/Enter: 확인", 220, 440, 20, GRAY)
