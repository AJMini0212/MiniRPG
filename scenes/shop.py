import pygame
from data.items import ITEMS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (40, 40, 40)
YELLOW = (255, 220, 0)
GREEN = (50, 200, 50)
RED = (220, 50, 50)
GRAY = (180, 180, 180)

SHOP_ITEMS = [
    {"key": "potion",    "price": 50},
    {"key": "hi_potion", "price": 120},
    {"key": "ether",     "price": 80},
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
        self.screen.fill((20, 20, 50))

        # 제목
        pygame.draw.rect(self.screen, DARK, (150, 40, 500, 60))
        pygame.draw.rect(self.screen, WHITE, (150, 40, 500, 60), 2)
        draw_text(self.screen, "상점", 360, 55, 32, YELLOW)

        # 아이템 목록
        for i, entry in enumerate(SHOP_ITEMS):
            item = ITEMS[entry["key"]]
            box_y = 130 + i * 70
            color = YELLOW if i == self.selected else WHITE
            bg = (60, 60, 90) if i == self.selected else DARK
            pygame.draw.rect(self.screen, bg, (150, box_y, 500, 58))
            pygame.draw.rect(self.screen, color, (150, box_y, 500, 58), 2)

            prefix = "▶ " if i == self.selected else "  "
            draw_text(self.screen, prefix + item["name"], 165, box_y + 8, 26, color)
            # 아이템 효과
            effect = f"HP+{item['hp']}" if item["hp"] > 0 else f"MP+{item['mp']}"
            draw_text(self.screen, effect, 380, box_y + 8, 22, GRAY)
            # 가격
            draw_text(self.screen, f"{entry['price']} G", 550, box_y + 8, 24, YELLOW)
            # 보유 수량
            owned = self.player.inventory.get(entry["key"], 0)
            draw_text(self.screen, f"보유 {owned}개", 165, box_y + 32, 20, GRAY)

        # 골드 표시
        pygame.draw.rect(self.screen, DARK, (150, 360, 500, 44))
        pygame.draw.rect(self.screen, WHITE, (150, 360, 500, 44), 2)
        draw_text(self.screen, f"소지 골드: {self.player.gold} G", 165, 370, 24, YELLOW)

        # 메시지창
        pygame.draw.rect(self.screen, DARK, (150, 415, 500, 50))
        pygame.draw.rect(self.screen, WHITE, (150, 415, 500, 50), 2)
        draw_text(self.screen, self.msg, 165, 426, 22, WHITE)

        # 조작 안내
        draw_text(self.screen, "Z/Enter: 구매    X: 나가기", 230, 455, 18, GRAY)
