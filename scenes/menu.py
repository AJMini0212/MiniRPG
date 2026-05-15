import pygame
from data.save_system import has_save

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
YELLOW = (255, 220, 0)
GRAY = (180, 180, 180)
DARK_BLUE = (80, 120, 180)
LIGHT_BLUE = (135, 195, 235)


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
        # 배경: 파란 그래디언트 효과
        for y in range(480):
            ratio = y / 480
            r = int(135 * (1 - ratio) + 100 * ratio)
            g = int(195 * (1 - ratio) + 150 * ratio)
            b = int(235 * (1 - ratio) + 200 * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (800, y))

        # 포켓볼 장식 (좌상단)
        pygame.draw.circle(self.screen, (220, 50, 50), (80, 60), 40)
        pygame.draw.circle(self.screen, WHITE, (80, 60), 35)
        pygame.draw.circle(self.screen, (220, 50, 50), (80, 60), 30)
        pygame.draw.line(self.screen, WHITE, (50, 60), (110, 60), 5)

        # 포켓볼 장식 (우하단)
        pygame.draw.circle(self.screen, (220, 50, 50), (720, 400), 35)
        pygame.draw.circle(self.screen, WHITE, (720, 400), 30)
        pygame.draw.circle(self.screen, (220, 50, 50), (720, 400), 25)
        pygame.draw.line(self.screen, WHITE, (695, 400), (745, 400), 4)

        # 제목
        draw_text(self.screen, "Mini RPG", 260, 60, 64, YELLOW)
        draw_text(self.screen, "게임에 오신 것을 환영합니다!", 200, 130, 24, WHITE)

        # 메뉴 아이템
        menu_y_start = 220
        for i, item in enumerate(self.menu_items):
            y = menu_y_start + i * 90
            color = YELLOW if i == self.selected else WHITE
            bg = (150, 80, 80) if i == self.selected else (100, 60, 60)

            # 버튼 박스 (빨간 테두리)
            pygame.draw.rect(self.screen, bg, (200, y, 400, 70))
            pygame.draw.rect(self.screen, RED, (200, y, 400, 70), 4)

            prefix = "▶ " if i == self.selected else "  "
            draw_text(self.screen, prefix + item, 240, y + 17, 36, color)

        # 조작 안내
        draw_text(self.screen, "위/아래: 선택  Z/Enter: 확인", 220, 450, 18, GRAY)
