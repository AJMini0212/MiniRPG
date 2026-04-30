import pygame
import random
from entities.monster import Monster
from data.items import ITEMS
from data.capture import attempt_catch

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
    pygame.draw.rect(screen, bg_color, (x, y, w, h))
    pygame.draw.rect(screen, BORDER, (x, y, w, h), 3)
    pygame.draw.rect(screen, BORDER, (x, y, w, 35))
    draw_text(screen, title, x + 15, y + 8, 22, YELLOW)


# 메뉴 상태
MENU_SELECT = "select"
MENU_MAIN = "main"

MAIN_ACTIONS = ["공격", "포획", "교체", "도망"]


class BattleScene:
    def __init__(self, screen, player, enemy_data):
        self.screen = screen
        self.player = player
        self.enemy_monster = Monster(enemy_data)

        # 플레이어가 몬스터를 보유하지 않으면 자동으로 몬스터 생성
        if not self.player.team:
            self.player_monster = Monster(enemy_data)
            self.player.team.append(self.player_monster)
        else:
            self.player_monster = self.player.team[0]

        self.menu = MENU_SELECT
        self.selected = 0
        self.log = [f"{self.enemy_monster.name}이(가) 나타났다!"]
        self.result = None
        self.catch_attempt = None  # (success, rate)

    def handle_event(self, event):
        if self.result or event.type != pygame.KEYDOWN:
            return

        if self.menu == MENU_SELECT:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.player.team)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.player.team)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                self.player_monster = self.player.team[self.selected]
                self.menu = MENU_MAIN
                self.selected = 0
                self.log = [f"{self.player_monster.name}을(를) 내보냈다!"]

        elif self.menu == MENU_MAIN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(MAIN_ACTIONS)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(MAIN_ACTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                self._execute_action()

    def _execute_action(self):
        action = MAIN_ACTIONS[self.selected]
        if action == "공격":
            self._player_attack()
        elif action == "포획":
            self._attempt_capture()
        elif action == "교체":
            self.menu = MENU_SELECT
            self.selected = 0
        elif action == "도망":
            if random.random() < 0.5:
                self.log = ["도망쳤다!"]
                self.result = "flee"
            else:
                self.log = ["도망에 실패했다!"]
                self._enemy_attack()

    def _player_attack(self):
        dmg = max(1, self.player_monster.attack - self.enemy_monster.defense + random.randint(-2, 2))
        self.enemy_monster.hp -= dmg
        self.log = [f"{self.player_monster.name}의 공격! {dmg} 데미지!"]
        self._check_enemy_dead() or self._enemy_attack()

    def _attempt_capture(self):
        success, rate = attempt_catch(self.enemy_monster)
        rate_percent = int(rate * 100)
        self.catch_attempt = (success, rate_percent)

        if success:
            ok, msg = self.player.catch_monster(self.enemy_monster)
            self.log = [msg]
            if ok:
                self.player.gain_team_exp(self.enemy_monster.exp_reward)
                self.log.append(f"경험치를 얻었다!")
                self.result = "catch"
            else:
                self.log = ["팀이 가득 찼다!"]
                self._enemy_attack()
        else:
            self.log = [f"포획 실패... ({rate_percent}% 확률)"]
            self._enemy_attack()

    def _check_enemy_dead(self):
        if not self.enemy_monster.is_alive():
            self.player.gain_team_exp(self.enemy_monster.exp_reward)
            self.log.append(f"{self.enemy_monster.name}을(를) 이겼다!")
            self.log.append(f"경험치를 얻었다!")
            self.result = "win"
            return True
        return False

    def _enemy_attack(self):
        dmg = max(1, self.enemy_monster.attack - self.player_monster.defense + random.randint(-2, 2))
        self.player_monster.hp -= dmg
        self.log.append(f"{self.enemy_monster.name}의 공격! {dmg} 데미지!")

        if self.player_monster.hp <= 0:
            self.player_monster.hp = 0
            self.log.append(f"{self.player_monster.name}이(가) 쓰러졌다!")

            # 다음 몬스터 자동 선택
            alive_monsters = [m for m in self.player.team if m.hp > 0]
            if alive_monsters:
                self.player_monster = alive_monsters[0]
                self.log.append(f"{self.player_monster.name}을(를) 내보냈다!")
            else:
                self.log.append("모든 몬스터가 쓰러졌다...")
                self.result = "lose"

    def draw(self):
        self.screen.fill(DARK2)

        # ===== 위: 몬스터 카드 =====
        # 적 몬스터
        draw_card(self.screen, 20, 20, 360, 140, f"{self.enemy_monster.name}", (60, 40, 40))
        pygame.draw.rect(self.screen, self.enemy_monster.color, (40, 60, 40, 40))
        draw_text(self.screen, f"Lv. {self.enemy_monster.level}", 90, 60, 18, YELLOW)
        draw_text(self.screen, f"HP", 90, 85, 18, CYAN)
        draw_bar(self.screen, 130, 85, self.enemy_monster.hp, self.enemy_monster.max_hp, 200, 18,
                 GREEN if self.enemy_monster.hp / self.enemy_monster.max_hp > 0.3 else RED)

        # 플레이어 몬스터
        draw_card(self.screen, 420, 20, 360, 140, f"{self.player_monster.name}", (40, 50, 80))
        pygame.draw.rect(self.screen, self.player_monster.color, (440, 60, 40, 40))
        draw_text(self.screen, f"Lv. {self.player_monster.level}", 490, 60, 18, YELLOW)
        draw_text(self.screen, f"HP", 490, 85, 18, CYAN)
        draw_bar(self.screen, 530, 85, self.player_monster.hp, self.player_monster.max_hp, 210, 18,
                 GREEN if self.player_monster.hp / self.player_monster.max_hp > 0.3 else RED)
        draw_text(self.screen, f"{self.player_monster.hp}/{self.player_monster.max_hp}", 745, 85, 16, WHITE)

        # 팀 상태
        draw_text(self.screen, f"팀 ({len(self.player.team)}/6)", 430, 110, 18, CYAN)
        for i, m in enumerate(self.player.team):
            x = 430 + i * 50
            bar_color = GREEN if m.hp > 0 else RED
            draw_bar(self.screen, x, 130, m.hp, m.max_hp, 45, 8, bar_color)

        # ===== 중간: 로그 =====
        pygame.draw.rect(self.screen, DARK, (20, 180, 760, 100))
        pygame.draw.rect(self.screen, BORDER, (20, 180, 760, 100), 2)
        draw_text(self.screen, "전투 로그", 30, 185, 18, YELLOW)
        for i, line in enumerate(self.log[-2:]):
            draw_text(self.screen, line, 35, 210 + i * 28, 20, WHITE)

        # ===== 아래: 메뉴 =====
        self._draw_menu()

        # ===== 결과 =====
        if self.result:
            overlay = pygame.Surface((800, 480), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            if self.result == "win":
                draw_text(self.screen, "승리!", 320, 140, 56, YELLOW)
            elif self.result == "catch":
                draw_text(self.screen, "포획!", 300, 140, 56, ORANGE)
            elif self.result == "lose":
                draw_text(self.screen, "패배...", 300, 170, 56, RED)
            elif self.result == "flee":
                draw_text(self.screen, "도망!", 320, 170, 56, WHITE)

            draw_text(self.screen, "Enter키로 계속", 290, 300, 28, CYAN)

    def _draw_menu(self):
        if self.menu == MENU_SELECT:
            menu_h = 30 + len(self.player.team) * 42
            pygame.draw.rect(self.screen, DARK, (20, 310, 760, menu_h))
            pygame.draw.rect(self.screen, BORDER, (20, 310, 760, menu_h), 2)
            draw_text(self.screen, "몬스터 선택", 30, 315, 18, YELLOW)

            for i, monster in enumerate(self.player.team):
                y = 350 + i * 42
                color = YELLOW if i == self.selected else WHITE
                bg = (80, 80, 120) if i == self.selected else DARK
                pygame.draw.rect(self.screen, bg, (50, y - 5, 700, 38))
                pygame.draw.rect(self.screen, color, (50, y - 5, 700, 38), 1)

                status = "살아있음" if monster.hp > 0 else "쓰러짐"
                status_color = GREEN if monster.hp > 0 else RED
                prefix = "▶ " if i == self.selected else "  "
                draw_text(self.screen, f"{prefix}{monster.name} Lv.{monster.level}", 60, y, 26, color)
                draw_text(self.screen, f"HP {monster.hp}/{monster.max_hp}  {status}", 380, y, 20, status_color)

        elif self.menu == MENU_MAIN:
            menu_h = 30 + len(MAIN_ACTIONS) * 42
            pygame.draw.rect(self.screen, DARK, (20, 310, 760, menu_h))
            pygame.draw.rect(self.screen, BORDER, (20, 310, 760, menu_h), 2)
            draw_text(self.screen, "액션 선택", 30, 315, 18, YELLOW)

            for i, action in enumerate(MAIN_ACTIONS):
                y = 350 + i * 42
                color = YELLOW if i == self.selected else WHITE
                bg = (80, 80, 120) if i == self.selected else DARK
                pygame.draw.rect(self.screen, bg, (50, y - 5, 700, 38))
                pygame.draw.rect(self.screen, color, (50, y - 5, 700, 38), 1)

                prefix = "▶ " if i == self.selected else "  "
                draw_text(self.screen, prefix + action, 60, y, 26, color)
