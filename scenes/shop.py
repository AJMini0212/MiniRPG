import pygame
from data.items import ITEMS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 0)
GREEN = (50, 200, 50)
RED = (220, 50, 50)
GRAY = (180, 180, 180)
LIGHT_BLUE = (135, 195, 235)
DARK_BLUE = (80, 120, 180)

SHOP_ITEMS = [
    {"key": "potion",         "price": 50},
    {"key": "hi_potion",      "price": 120},
    {"key": "full_potion",    "price": 200},
    {"key": "ether",          "price": 80},
    {"key": "full_ether",     "price": 200},
    {"key": "full_recovery",  "price": 500},
]


def draw_text(screen, text, x, y, size=24, color=WHITE):
    font = pygame.font.SysFont("malgungothic", size)
    screen.blit(font.render(text, True, color), (x, y))


class ShopScene:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.selected = 0
        self.gold = player.gold
        self.msg = "어서오세요! 무엇을 사시겠어요?"

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(SHOP_ITEMS)
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(SHOP_ITEMS)
        elif event.key in (pygame.K_RETURN, pygame.K_z):
            self._buy()
        elif event.key == pygame.K_x:
            return "exit"

    def _buy(self):
        entry = SHOP_ITEMS[self.selected]
        if self.player.gold < entry["price"]:
            self.msg = "골드가 부족합니다!"
        else:
            self.player.gold -= entry["price"]
            self.player.inventory[entry["key"]] = self.player.inventory.get(entry["key"], 0) + 1
            item_name = ITEMS[entry["key"]]["name"]
            self.msg = f"{item_name}을(를) 구매했습니다!"

    def draw(self):
        # 배경: 파란 그래디언트
        for y in range(480):
            ratio = y / 480
            r = int(135 * (1 - ratio) + 80 * ratio)
            g = int(195 * (1 - ratio) + 120 * ratio)
            b = int(235 * (1 - ratio) + 180 * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (800, y))

        # 제목 패널
        pygame.draw.rect(self.screen, (45, 45, 60), (50, 10, 700, 50))
        pygame.draw.rect(self.screen, (100, 100, 120), (50, 10, 700, 50), 3)
        draw_text(self.screen, "포켓몬 센터 - 아이템 판매", 80, 20, 32, YELLOW)

        # 아이템 목록
        for i, entry in enumerate(SHOP_ITEMS):
            item = ITEMS[entry["key"]]
            box_y = 75 + i * 55
            color = YELLOW if i == self.selected else WHITE
            bg = (100, 70, 70) if i == self.selected else (50, 45, 55)

            pygame.draw.rect(self.screen, bg, (50, box_y, 700, 50))
            pygame.draw.rect(self.screen, RED if i == self.selected else (100, 100, 120), (50, box_y, 700, 50), 2)

            prefix = "▶ " if i == self.selected else "  "
            draw_text(self.screen, prefix + item["name"], 70, box_y + 8, 22, color)
            effect = f"HP+{item['hp']}" if item["hp"] > 0 else f"MP+{item['mp']}"
            draw_text(self.screen, effect, 350, box_y + 8, 18, GRAY)
            draw_text(self.screen, f"{entry['price']}G", 550, box_y + 8, 20, YELLOW)
            owned = self.player.inventory.get(entry["key"], 0)
            draw_text(self.screen, f"×{owned}", 650, box_y + 8, 18, GRAY)

        # 골드 표시
        pygame.draw.rect(self.screen, (45, 45, 60), (50, 405, 700, 35))
        pygame.draw.rect(self.screen, (100, 100, 120), (50, 405, 700, 35), 2)
        draw_text(self.screen, f"소지 골드: {self.player.gold} G", 70, 412, 22, YELLOW)

        # 메시지창
        if self.msg:
            pygame.draw.rect(self.screen, (45, 45, 60), (50, 445, 700, 30))
            pygame.draw.rect(self.screen, (100, 100, 120), (50, 445, 700, 30), 2)
            draw_text(self.screen, self.msg, 70, 450, 18, WHITE)

        # 조작 안내
        draw_text(self.screen, "위/아래: 선택   Z/Enter: 구매   X: 나가기", 180, 10, 14, GRAY)
