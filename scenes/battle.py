import pygame
import random
from entities.monster import Monster

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
GRAY = (180, 180, 180)
DARK = (40, 40, 40)
YELLOW = (255, 220, 0)


def draw_text(screen, text, x, y, size=24, color=BLACK):
    font = pygame.font.SysFont("malgungothic", size)
    screen.blit(font.render(text, True, color), (x, y))


def draw_hp_bar(screen, x, y, current, maximum, width=200):
    pygame.draw.rect(screen, GRAY, (x, y, width, 16))
    ratio = max(0, current / maximum)
    color = GREEN if ratio > 0.5 else RED
    pygame.draw.rect(screen, color, (x, y, int(width * ratio), 16))
    pygame.draw.rect(screen, BLACK, (x, y, width, 16), 2)


class BattleScene:
    ACTIONS = ["공격", "도망"]

    def __init__(self, screen, player, monster_data):
        self.screen = screen
        self.player = player
        self.monster = Monster(monster_data)
        self.selected = 0
        self.log = [f"{self.monster.name}이(가) 나타났다!"]
        self.result = None  # "win" | "lose" | "flee"
        self.turn = "player"
        self.animating = False

    def handle_event(self, event):
        if self.result or self.animating:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.ACTIONS)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.ACTIONS)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_z:
                self._execute_action()

    def _execute_action(self):
        action = self.ACTIONS[self.selected]
        if action == "공격":
            self._player_attack()
        elif action == "도망":
            self.log = ["도망쳤다!"]
            self.result = "flee"

    def _player_attack(self):
        dmg = max(1, self.player.attack - self.monster.defense + random.randint(-2, 2))
        self.monster.hp -= dmg
        self.log = [f"플레이어의 공격! {self.monster.name}에게 {dmg} 데미지!"]
        if not self.monster.is_alive():
            self.player.gain_exp(self.monster.exp)
            self.log.append(f"{self.monster.name}을(를) 쓰러뜨렸다!")
            self.log.append(f"경험치 +{self.monster.exp}")
            self.result = "win"
        else:
            self._monster_attack()

    def _monster_attack(self):
        dmg = max(1, self.monster.attack - self.player.defense + random.randint(-2, 2))
        self.player.hp -= dmg
        self.log.append(f"{self.monster.name}의 반격! {dmg} 데미지!")
        if self.player.hp <= 0:
            self.player.hp = 0
            self.log.append("플레이어가 쓰러졌다...")
            self.result = "lose"

    def draw(self):
        self.screen.fill((30, 30, 60))

        # 몬스터
        pygame.draw.rect(self.screen, self.monster.color, (480, 80, 80, 80))
        draw_text(self.screen, self.monster.name, 460, 50, 26, WHITE)
        draw_hp_bar(self.screen, 440, 170, self.monster.hp, self.monster.max_hp)
        draw_text(self.screen, f"HP {self.monster.hp}/{self.monster.max_hp}", 440, 190, 20, WHITE)

        # 플레이어
        pygame.draw.rect(self.screen, (50, 100, 255), (120, 200, 80, 80))
        draw_text(self.screen, "플레이어", 100, 170, 26, WHITE)
        draw_hp_bar(self.screen, 80, 290, self.player.hp, self.player.max_hp)
        draw_text(self.screen, f"HP {self.player.hp}/{self.player.max_hp}", 80, 310, 20, WHITE)
        draw_text(self.screen, f"Lv.{self.player.level}", 80, 335, 20, YELLOW)

        # 로그창
        pygame.draw.rect(self.screen, DARK, (20, 360, 760, 90))
        pygame.draw.rect(self.screen, WHITE, (20, 360, 760, 90), 2)
        for i, line in enumerate(self.log[-2:]):
            draw_text(self.screen, line, 30, 370 + i * 30, 22, WHITE)

        # 액션 메뉴
        pygame.draw.rect(self.screen, DARK, (560, 260, 220, 90))
        pygame.draw.rect(self.screen, WHITE, (560, 260, 220, 90), 2)
        for i, action in enumerate(self.ACTIONS):
            color = YELLOW if i == self.selected else WHITE
            prefix = "▶ " if i == self.selected else "  "
            draw_text(self.screen, prefix + action, 570, 270 + i * 34, 26, color)

        # 결과 오버레이
        if self.result:
            overlay = pygame.Surface((800, 480), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))
            if self.result == "win":
                draw_text(self.screen, "승리!", 340, 200, 48, YELLOW)
            elif self.result == "lose":
                draw_text(self.screen, "패배...", 320, 200, 48, RED)
            elif self.result == "flee":
                draw_text(self.screen, "도망!", 340, 200, 48, WHITE)
            draw_text(self.screen, "Enter키로 계속", 300, 270, 28, WHITE)
