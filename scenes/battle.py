import pygame
import random
from entities.monster import Monster
from data.items import ITEMS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (80, 160, 255)
GRAY = (180, 180, 180)
DARK = (40, 40, 40)
YELLOW = (255, 220, 0)
ORANGE = (255, 160, 0)


def draw_text(screen, text, x, y, size=24, color=BLACK):
    font = pygame.font.SysFont("malgungothic", size)
    screen.blit(font.render(text, True, color), (x, y))


def draw_bar(screen, x, y, current, maximum, width, color):
    pygame.draw.rect(screen, GRAY, (x, y, width, 14))
    ratio = max(0, current / maximum)
    pygame.draw.rect(screen, color, (x, y, int(width * ratio), 14))
    pygame.draw.rect(screen, WHITE, (x, y, width, 14), 1)


# 메뉴 상태
MENU_MAIN = "main"
MENU_SKILL = "skill"
MENU_ITEM = "item"

MAIN_ACTIONS = ["공격", "스킬", "아이템", "도망"]


class BattleScene:
    def __init__(self, screen, player, monster_data):
        self.screen = screen
        self.player = player
        self.monster = Monster(monster_data)
        self.menu = MENU_MAIN
        self.selected = 0
        self.log = [f"{self.monster.name}이(가) 나타났다!"]
        self.result = None
        self.level_up_msg = None

    def _current_list(self):
        if self.menu == MENU_MAIN:
            return MAIN_ACTIONS
        elif self.menu == MENU_SKILL:
            return self.player.skills
        elif self.menu == MENU_ITEM:
            return [k for k, v in self.player.inventory.items() if v > 0]
        return []

    def handle_event(self, event):
        if self.result or event.type != pygame.KEYDOWN:
            return
        lst = self._current_list()
        if not lst:
            return

        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(lst)
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(lst)
        elif event.key in (pygame.K_RETURN, pygame.K_z):
            self._confirm()
        elif event.key == pygame.K_x:
            if self.menu != MENU_MAIN:
                self.menu = MENU_MAIN
                self.selected = 0

    def _confirm(self):
        if self.menu == MENU_MAIN:
            action = MAIN_ACTIONS[self.selected]
            if action == "공격":
                self._player_attack()
            elif action == "스킬":
                self.menu = MENU_SKILL
                self.selected = 0
            elif action == "아이템":
                items = [k for k, v in self.player.inventory.items() if v > 0]
                if not items:
                    self.log = ["아이템이 없다!"]
                else:
                    self.menu = MENU_ITEM
                    self.selected = 0
            elif action == "도망":
                self.log = ["도망쳤다!"]
                self.result = "flee"

        elif self.menu == MENU_SKILL:
            skill = self.player.skills[self.selected]
            if self.player.mp < skill["mp_cost"]:
                self.log = ["MP가 부족하다!"]
            else:
                self._use_skill(skill)
                self.menu = MENU_MAIN
                self.selected = 0

        elif self.menu == MENU_ITEM:
            items = [k for k, v in self.player.inventory.items() if v > 0]
            key = items[self.selected]
            ok, msgs = self.player.use_item(key)
            self.log = msgs if isinstance(msgs, list) else [msgs]
            self.menu = MENU_MAIN
            self.selected = 0
            if ok:
                self._monster_attack()

    def _player_attack(self):
        self.player.guarding = False
        dmg = max(1, self.player.attack - self.monster.defense + random.randint(-2, 2))
        self.monster.hp -= dmg
        self.log = [f"플레이어의 공격! {dmg} 데미지!"]
        self._check_monster_dead() or self._monster_attack()

    def _use_skill(self, skill):
        self.player.guarding = False
        self.player.mp -= skill["mp_cost"]
        if skill["type"] == "attack":
            dmg = max(1, int(self.player.attack * skill["power"]) - self.monster.defense + random.randint(-2, 2))
            self.monster.hp -= dmg
            self.log = [f"{skill['name']}! {self.monster.name}에게 {dmg} 데미지!"]
            self._check_monster_dead() or self._monster_attack()
        elif skill["type"] == "magic":
            dmg = max(1, int(self.player.attack * skill["power"]) + random.randint(0, 5))
            self.monster.hp -= dmg
            self.log = [f"{skill['name']}! {self.monster.name}에게 {dmg} 데미지! (방어 무시)"]
            self._check_monster_dead() or self._monster_attack()
        elif skill["type"] == "defend":
            self.player.guarding = True
            self.log = ["방어 태세를 취했다!"]
            self._monster_attack()
        elif skill["type"] == "heal":
            heal_amount = min(25, self.player.max_hp - self.player.hp)
            self.player.hp += heal_amount
            self.log = [f"{skill['name']}! HP +{heal_amount}"]
            self._monster_attack()

    def _check_monster_dead(self):
        if not self.monster.is_alive():
            prev_level = self.player.level
            self.player.gain_exp(self.monster.exp)
            self.log.append(f"{self.monster.name}을(를) 쓰러뜨렸다!")
            self.log.append(f"경험치 +{self.monster.exp}")
            if self.player.level > prev_level:
                self.level_up_msg = f"레벨 업! Lv.{self.player.level}"
            self.result = "win"
            return True
        return False

    def _monster_attack(self):
        defense = self.player.defense * 2 if self.player.guarding else self.player.defense
        dmg = max(1, self.monster.attack - defense + random.randint(-2, 2))
        self.player.hp -= dmg
        guard_txt = " (방어!)" if self.player.guarding else ""
        self.log.append(f"{self.monster.name}의 공격! {dmg} 데미지{guard_txt}")
        self.player.guarding = False
        if self.player.hp <= 0:
            self.player.hp = 0
            self.log.append("플레이어가 쓰러졌다...")
            self.result = "lose"

    def draw(self):
        self.screen.fill((30, 30, 60))

        # 몬스터
        pygame.draw.rect(self.screen, self.monster.color, (480, 80, 80, 80))
        draw_text(self.screen, self.monster.name, 460, 50, 26, WHITE)
        draw_bar(self.screen, 440, 172, self.monster.hp, self.monster.max_hp, 200, GREEN if self.monster.hp / self.monster.max_hp > 0.5 else RED)
        draw_text(self.screen, f"HP {self.monster.hp}/{self.monster.max_hp}", 440, 190, 20, WHITE)

        # 플레이어
        pygame.draw.rect(self.screen, (50, 100, 255), (120, 200, 80, 80))
        draw_text(self.screen, "플레이어", 100, 170, 26, WHITE)
        draw_bar(self.screen, 80, 292, self.player.hp, self.player.max_hp, 200, GREEN if self.player.hp / self.player.max_hp > 0.5 else RED)
        draw_text(self.screen, f"HP {self.player.hp}/{self.player.max_hp}", 80, 308, 20, WHITE)
        draw_bar(self.screen, 80, 328, self.player.mp, self.player.max_mp, 200, BLUE)
        draw_text(self.screen, f"MP {self.player.mp}/{self.player.max_mp}", 80, 344, 20, WHITE)
        draw_text(self.screen, f"Lv.{self.player.level}", 290, 308, 20, YELLOW)

        # 로그창
        pygame.draw.rect(self.screen, DARK, (20, 368, 540, 90))
        pygame.draw.rect(self.screen, WHITE, (20, 368, 540, 90), 2)
        for i, line in enumerate(self.log[-2:]):
            draw_text(self.screen, line, 30, 378 + i * 30, 21, WHITE)

        # 메뉴
        self._draw_menu()

        # 결과 오버레이
        if self.result:
            overlay = pygame.Surface((800, 480), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            if self.result == "win":
                draw_text(self.screen, "승리!", 340, 180, 52, YELLOW)
                if self.level_up_msg:
                    draw_text(self.screen, self.level_up_msg, 290, 245, 32, ORANGE)
            elif self.result == "lose":
                draw_text(self.screen, "패배...", 310, 190, 52, RED)
            elif self.result == "flee":
                draw_text(self.screen, "도망!", 340, 190, 52, WHITE)
            draw_text(self.screen, "Enter키로 계속", 290, 300, 28, WHITE)

    def _draw_menu(self):
        mx, my, mw, mh = 572, 260, 210, 0

        if self.menu == MENU_MAIN:
            mh = 30 + len(MAIN_ACTIONS) * 34
            pygame.draw.rect(self.screen, DARK, (mx, my, mw, mh))
            pygame.draw.rect(self.screen, WHITE, (mx, my, mw, mh), 2)
            for i, action in enumerate(MAIN_ACTIONS):
                color = YELLOW if i == self.selected else WHITE
                prefix = "▶ " if i == self.selected else "  "
                draw_text(self.screen, prefix + action, mx + 10, my + 10 + i * 34, 26, color)

        elif self.menu == MENU_SKILL:
            skills = self.player.skills
            mh = 30 + len(skills) * 34
            pygame.draw.rect(self.screen, DARK, (mx, my, mw, mh))
            pygame.draw.rect(self.screen, WHITE, (mx, my, mw, mh), 2)
            draw_text(self.screen, "[ 스킬 ]", mx + 10, my + 4, 20, YELLOW)
            for i, sk in enumerate(skills):
                color = YELLOW if i == self.selected else WHITE
                mp_color = BLUE if self.player.mp >= sk["mp_cost"] else RED
                prefix = "▶ " if i == self.selected else "  "
                draw_text(self.screen, prefix + sk["name"], mx + 10, my + 26 + i * 34, 22, color)
                draw_text(self.screen, f"MP:{sk['mp_cost']}", mx + 140, my + 26 + i * 34, 20, mp_color)
            draw_text(self.screen, "X: 뒤로", mx + 10, my + mh - 22, 18, GRAY)

        elif self.menu == MENU_ITEM:
            items = [k for k, v in self.player.inventory.items() if v > 0]
            mh = 30 + max(len(items), 1) * 34
            pygame.draw.rect(self.screen, DARK, (mx, my, mw, mh))
            pygame.draw.rect(self.screen, WHITE, (mx, my, mw, mh), 2)
            draw_text(self.screen, "[ 아이템 ]", mx + 10, my + 4, 20, YELLOW)
            for i, key in enumerate(items):
                item = ITEMS[key]
                color = YELLOW if i == self.selected else WHITE
                prefix = "▶ " if i == self.selected else "  "
                draw_text(self.screen, f"{prefix}{item['name']} x{self.player.inventory[key]}", mx + 10, my + 26 + i * 34, 22, color)
            draw_text(self.screen, "X: 뒤로", mx + 10, my + mh - 22, 18, GRAY)
