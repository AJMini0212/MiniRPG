import pygame
import random
from entities.monster import Monster
from data.items import ITEMS

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (100, 180, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
DARK = (40, 40, 40)
DARK2 = (30, 30, 50)
YELLOW = (255, 220, 0)
ORANGE = (255, 160, 0)
CYAN = (100, 220, 220)
BORDER = (150, 150, 200)


def draw_text(screen, text, x, y, size=24, color=WHITE):
    font = pygame.font.SysFont("malgungothic", size)
    screen.blit(font.render(text, True, color), (x, y))


def draw_bar(screen, x, y, current, maximum, width, height, color):
    pygame.draw.rect(screen, DARK_GRAY, (x, y, width, height))
    if maximum > 0:
        ratio = max(0, min(1, current / maximum))
        pygame.draw.rect(screen, color, (x, y, int(width * ratio), height))
    pygame.draw.rect(screen, BORDER, (x, y, width, height), 2)


def draw_card(screen, x, y, w, h, title, bg_color):
    """정보 카드 배경"""
    pygame.draw.rect(screen, bg_color, (x, y, w, h))
    pygame.draw.rect(screen, BORDER, (x, y, w, h), 3)
    pygame.draw.rect(screen, BORDER, (x, y, w, 35))
    draw_text(screen, title, x + 15, y + 8, 22, YELLOW)


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
        self.screen.fill(DARK2)

        # ===== 위: 몬스터/플레이어 정보 카드 =====
        # 몬스터 카드 (좌측)
        draw_card(self.screen, 20, 20, 360, 140, f"{self.monster.name}", (60, 40, 40))

        # 몬스터 색상 표시
        pygame.draw.rect(self.screen, self.monster.color, (40, 60, 40, 40))

        # 몬스터 스탯
        draw_text(self.screen, f"HP", 90, 60, 20, CYAN)
        draw_bar(self.screen, 130, 60, self.monster.hp, self.monster.max_hp, 200, 20, GREEN if self.monster.hp / self.monster.max_hp > 0.3 else RED)
        draw_text(self.screen, f"{self.monster.hp}/{self.monster.max_hp}", 340, 60, 18, WHITE)

        draw_text(self.screen, f"ATK: {self.monster.attack}  DEF: {self.monster.defense}", 90, 90, 18, GRAY)
        draw_text(self.screen, f"경험치: {self.monster.exp}", 90, 115, 18, YELLOW)

        # 플레이어 카드 (우측)
        draw_card(self.screen, 420, 20, 360, 140, "플레이어", (40, 50, 80))

        # 플레이어 색상 표시
        pygame.draw.rect(self.screen, (50, 100, 255), (440, 60, 40, 40))

        # 플레이어 스탯
        draw_text(self.screen, f"Lv. {self.player.level}", 490, 60, 20, YELLOW)

        draw_text(self.screen, f"HP", 490, 90, 18, CYAN)
        draw_bar(self.screen, 530, 90, self.player.hp, self.player.max_hp, 210, 18, GREEN if self.player.hp / self.player.max_hp > 0.3 else RED)
        draw_text(self.screen, f"{self.player.hp}/{self.player.max_hp}", 745, 90, 16, WHITE)

        draw_text(self.screen, f"MP", 490, 115, 18, CYAN)
        draw_bar(self.screen, 530, 115, self.player.mp, self.player.max_mp, 210, 18, BLUE)
        draw_text(self.screen, f"{self.player.mp}/{self.player.max_mp}", 745, 115, 16, WHITE)

        # ===== 중간: 전투 로그 =====
        pygame.draw.rect(self.screen, DARK, (20, 180, 760, 120))
        pygame.draw.rect(self.screen, BORDER, (20, 180, 760, 120), 2)
        draw_text(self.screen, "전투 로그", 30, 185, 18, YELLOW)

        for i, line in enumerate(self.log[-3:]):
            draw_text(self.screen, line, 35, 210 + i * 30, 20, WHITE)

        # ===== 아래: 액션 메뉴 =====
        self._draw_menu()

        # ===== 결과 오버레이 =====
        if self.result:
            overlay = pygame.Surface((800, 480), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            if self.result == "win":
                draw_text(self.screen, "승리!", 320, 140, 56, YELLOW)
                if self.level_up_msg:
                    draw_text(self.screen, self.level_up_msg, 250, 210, 36, ORANGE)
            elif self.result == "lose":
                draw_text(self.screen, "패배...", 300, 170, 56, RED)
            elif self.result == "flee":
                draw_text(self.screen, "도망!", 320, 170, 56, WHITE)

            draw_text(self.screen, "Enter키로 계속", 290, 300, 28, CYAN)

    def _draw_menu(self):
        if self.menu == MENU_MAIN:
            menu_h = 30 + len(MAIN_ACTIONS) * 42
            pygame.draw.rect(self.screen, DARK, (20, 320, 760, menu_h))
            pygame.draw.rect(self.screen, BORDER, (20, 320, 760, menu_h), 2)
            draw_text(self.screen, "액션 선택", 30, 325, 18, YELLOW)

            cols = 2
            for i, action in enumerate(MAIN_ACTIONS):
                row = i // cols
                col = i % cols
                x = 50 + col * 380
                y = 360 + row * 42

                color = YELLOW if i == self.selected else WHITE
                bg = (80, 80, 120) if i == self.selected else DARK
                pygame.draw.rect(self.screen, bg, (x - 10, y - 5, 350, 38))
                pygame.draw.rect(self.screen, color, (x - 10, y - 5, 350, 38), 1)

                prefix = "▶ " if i == self.selected else "  "
                draw_text(self.screen, prefix + action, x, y, 28, color)

        elif self.menu == MENU_SKILL:
            skills = self.player.skills
            menu_h = 30 + len(skills) * 38
            pygame.draw.rect(self.screen, DARK, (20, 320, 760, menu_h))
            pygame.draw.rect(self.screen, BORDER, (20, 320, 760, menu_h), 2)
            draw_text(self.screen, "[ 스킬 ]", 30, 325, 18, YELLOW)

            for i, sk in enumerate(skills):
                y = 360 + i * 38
                color = YELLOW if i == self.selected else WHITE
                mp_ok = self.player.mp >= sk["mp_cost"]
                mp_color = BLUE if mp_ok else RED

                bg = (80, 80, 120) if i == self.selected else DARK
                pygame.draw.rect(self.screen, bg, (50, y - 5, 700, 35))
                pygame.draw.rect(self.screen, color, (50, y - 5, 700, 35), 1)

                prefix = "▶ " if i == self.selected else "  "
                draw_text(self.screen, prefix + sk["name"], 60, y, 24, color)
                draw_text(self.screen, f"MP:{sk['mp_cost']}", 320, y, 20, mp_color)
                draw_text(self.screen, sk["description"], 420, y, 18, GRAY)

        elif self.menu == MENU_ITEM:
            items = [k for k, v in self.player.inventory.items() if v > 0]
            menu_h = 30 + len(items) * 38
            pygame.draw.rect(self.screen, DARK, (20, 320, 760, menu_h))
            pygame.draw.rect(self.screen, BORDER, (20, 320, 760, menu_h), 2)
            draw_text(self.screen, "[ 아이템 ]", 30, 325, 18, YELLOW)

            for i, key in enumerate(items):
                item = ITEMS[key]
                y = 360 + i * 38
                color = YELLOW if i == self.selected else WHITE

                bg = (80, 80, 120) if i == self.selected else DARK
                pygame.draw.rect(self.screen, bg, (50, y - 5, 700, 35))
                pygame.draw.rect(self.screen, color, (50, y - 5, 700, 35), 1)

                prefix = "▶ " if i == self.selected else "  "
                draw_text(self.screen, f"{prefix}{item['name']} x{self.player.inventory[key]}", 60, y, 24, color)

                effect = f"HP+{item['hp']}" if item["hp"] > 0 else f"MP+{item['mp']}"
                draw_text(self.screen, effect, 420, y, 20, CYAN)
