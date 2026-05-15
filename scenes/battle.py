import pygame
import random
from entities.monster import Monster
from data.items import ITEMS
from data.capture import attempt_catch
from effects.effects import EffectManager

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
        self.effects = EffectManager()

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

        # 효과 추가 (적 스프라이트 위치)
        self.effects.add_particles(590, 110, 12, (255, 150, 100), 40)
        self.effects.add_damage_number(590, 80, dmg)
        self.effects.shake_screen(4, 8)

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
                # 포획 성공 이펙트 (적 스프라이트 위치)
                self.effects.capture_effect(590, 110)
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

        # 데미지 숫자 효과 (플레이어 스프라이트 위치)
        self.effects.add_particles(150, 220, 10, (255, 100, 100), 35)
        self.effects.add_damage_number(150, 190, dmg, is_critical=False)
        self.effects.shake_screen(3, 6)

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
        self.effects.update()

        # ===== 배경 =====
        pygame.draw.rect(self.screen, (135, 195, 235), (0, 0, 800, 140))    # 하늘색
        pygame.draw.rect(self.screen, (100, 180, 80), (0, 140, 800, 90))    # 풀밭
        pygame.draw.rect(self.screen, (180, 150, 90), (0, 200, 800, 90))    # 바닥
        pygame.draw.rect(self.screen, (40, 35, 45), (0, 290, 800, 190))     # UI 배경

        # ===== 적 스프라이트 (우상단) =====
        pygame.draw.rect(self.screen, self.enemy_monster.color, (540, 60, 100, 100))

        # ===== 플레이어 스프라이트 (좌하단) =====
        pygame.draw.rect(self.screen, self.player_monster.color, (50, 170, 100, 100))

        # ===== 적 정보창 (좌상단) =====
        self._draw_info_panel(10, 12, 280, 85, self.enemy_monster, False)

        # ===== 플레이어 정보창 (우하단) =====
        self._draw_info_panel(430, 185, 355, 100, self.player_monster, True)

        # ===== 로그창 (하단 왼쪽) =====
        pygame.draw.rect(self.screen, (60, 50, 60), (0, 290, 400, 190))
        draw_text(self.screen, "전투 로그", 15, 300, 16, YELLOW)
        for i, line in enumerate(self.log[-2:]):
            draw_text(self.screen, line, 15, 330 + i * 30, 18, WHITE)

        # ===== 아래: 메뉴 =====
        self._draw_menu()

        # ===== 효과 =====
        self.effects.draw(self.screen)

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

    def _draw_info_panel(self, x, y, w, h, monster, show_team=False):
        """포켓몬 스타일 정보창 그리기"""
        # 배경 (둥근 사각형 효과)
        pygame.draw.rect(self.screen, (45, 45, 60), (x, y, w, h))
        pygame.draw.rect(self.screen, (100, 100, 120), (x, y, w, h), 2)

        # 이름과 레벨
        draw_text(self.screen, monster.name, x + 10, y + 10, 20, WHITE)
        draw_text(self.screen, f"Lv.{monster.level}", x + w - 80, y + 10, 18, YELLOW)

        # HP 바
        hp_ratio = max(0, min(1, monster.hp / monster.max_hp))
        bar_color = GREEN if hp_ratio > 0.3 else RED
        pygame.draw.rect(self.screen, (60, 60, 60), (x + 10, y + 40, w - 20, 12))
        pygame.draw.rect(self.screen, bar_color, (x + 10, y + 40, int((w - 20) * hp_ratio), 12))
        pygame.draw.rect(self.screen, (100, 100, 120), (x + 10, y + 40, w - 20, 12), 1)

        if show_team:
            # HP 수치
            draw_text(self.screen, f"{monster.hp}/{monster.max_hp}", x + 10, y + 58, 14, WHITE)

            # EXP 바
            exp_ratio = max(0, min(1, monster.exp / monster.exp_to_level))
            pygame.draw.rect(self.screen, (40, 40, 60), (x + 10, y + 76, w - 20, 8))
            pygame.draw.rect(self.screen, (100, 150, 255), (x + 10, y + 76, int((w - 20) * exp_ratio), 8))
            pygame.draw.rect(self.screen, (100, 100, 120), (x + 10, y + 76, w - 20, 8), 1)

    def _draw_menu(self):
        if self.menu == MENU_SELECT:
            # 팀 선택 메뉴: 3×2 그리드로 6마리 표시
            pygame.draw.rect(self.screen, (60, 50, 60), (0, 290, 800, 190))
            draw_text(self.screen, "몬스터 선택", 15, 300, 16, YELLOW)

            cols, rows = 3, 2
            for i, monster in enumerate(self.player.team):
                col = i % cols
                row = i // cols
                box_x = col * 267 + 10
                box_y = row * 85 + 335
                box_w, box_h = 255, 80

                color = YELLOW if i == self.selected else WHITE
                bg = (80, 80, 100) if i == self.selected else (50, 45, 55)
                pygame.draw.rect(self.screen, bg, (box_x, box_y, box_w, box_h))
                pygame.draw.rect(self.screen, color, (box_x, box_y, box_w, box_h), 2)

                status = "살아있음" if monster.hp > 0 else "쓰러짐"
                status_color = GREEN if monster.hp > 0 else RED
                prefix = "▶ " if i == self.selected else "  "
                draw_text(self.screen, f"{prefix}{monster.name}", box_x + 10, box_y + 8, 18, color)
                draw_text(self.screen, f"Lv.{monster.level}", box_x + 10, box_y + 28, 14, YELLOW)
                draw_text(self.screen, f"HP {monster.hp}/{monster.max_hp}", box_x + 10, box_y + 50, 12, status_color)

        elif self.menu == MENU_MAIN:
            # 액션 메뉴: 2×2 그리드 (공격, 포획, 교체, 도망)
            pygame.draw.rect(self.screen, (60, 50, 60), (400, 290, 400, 190))
            pygame.draw.rect(self.screen, (200, 50, 50), (400, 290, 400, 190), 3)
            draw_text(self.screen, "액션", 420, 300, 16, YELLOW)

            actions = [MAIN_ACTIONS[i] if i < len(MAIN_ACTIONS) else "" for i in range(4)]
            for i, action in enumerate(actions):
                col = i % 2
                row = i // 2
                box_x = 400 + col * 200 + 5
                box_y = 290 + row * 95 + 35
                box_w, box_h = 190, 85

                color = YELLOW if i == self.selected else WHITE
                bg = (100, 70, 70) if i == self.selected else (50, 45, 55)
                pygame.draw.rect(self.screen, bg, (box_x, box_y, box_w, box_h))
                pygame.draw.rect(self.screen, color, (box_x, box_y, box_w, box_h), 2)

                prefix = "▶ " if i == self.selected else "  "
                draw_text(self.screen, prefix + action, box_x + 15, box_y + 30, 22, color)
