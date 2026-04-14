import pygame
import random
from entities.player import Player
from data.monsters import MONSTERS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 0)
GRAY = (180, 180, 180)

TILE_SIZE = 32
GRASS_COLOR = (80, 160, 80)
DARK_GRASS_COLOR = (60, 120, 60)
TOWN_COLOR = (180, 150, 100)
TOWN_DARK_COLOR = (160, 130, 80)
ROAD_COLOR = (200, 180, 130)
ENCOUNTER_CHANCE = 0.004

# 맵 크기 (타일 단위)
MAP_COLS = 25
MAP_ROWS = 15
MAP_W = MAP_COLS * TILE_SIZE  # 800
MAP_H = MAP_ROWS * TILE_SIZE  # 480

# 마을 영역 (타일 단위)
TOWN_RECT = pygame.Rect(2, 2, 8, 6)  # 좌상단 마을

# NPC 위치 (픽셀)
NPC_X = 5 * TILE_SIZE
NPC_Y = 4 * TILE_SIZE
NPC_SIZE = 28
TALK_RANGE = 60


def draw_text(screen, text, x, y, size=22, color=BLACK):
    font = pygame.font.SysFont("malgungothic", size)
    screen.blit(font.render(text, True, color), (x, y))


class WorldScene:
    def __init__(self, screen, player=None):
        self.screen = screen
        self.player = player if player else Player(MAP_W // 2, MAP_H // 2)
        self.encounter = None
        self.open_shop = False
        self.talk_hint = False
        self._build_map()

    def _build_map(self):
        self.tiles = []
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if TOWN_RECT.collidepoint(c, r):
                    color = TOWN_COLOR if (r + c) % 2 == 0 else TOWN_DARK_COLOR
                else:
                    color = GRASS_COLOR if (r + c) % 2 == 0 else DARK_GRASS_COLOR
                self.tiles.append((c * TILE_SIZE, r * TILE_SIZE, color))

    def _in_town(self):
        px, py = self.player.x // TILE_SIZE, self.player.y // TILE_SIZE
        return TOWN_RECT.collidepoint(px, py)

    def _near_npc(self):
        dx = self.player.x - NPC_X
        dy = self.player.y - NPC_Y
        return (dx * dx + dy * dy) ** 0.5 < TALK_RANGE

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_z:
                if self._near_npc():
                    self.open_shop = True
            elif event.key == pygame.K_ESCAPE:
                return "menu"

    def update(self):
        keys = pygame.key.get_pressed()
        old_x, old_y = self.player.x, self.player.y
        self.player.handle_input(keys)

        # 맵 경계 처리
        self.player.x = max(0, min(self.player.x, MAP_W - 32))
        self.player.y = max(0, min(self.player.y, MAP_H - 32))
        self.player.rect.topleft = (self.player.x, self.player.y)

        self.talk_hint = self._near_npc()

        moving = any([
            keys[pygame.K_UP], keys[pygame.K_DOWN],
            keys[pygame.K_LEFT], keys[pygame.K_RIGHT],
        ])
        # 마을 안에서는 인카운터 없음
        if moving and not self._in_town() and random.random() < ENCOUNTER_CHANCE:
            self.encounter = random.choice(list(MONSTERS.values()))

    def draw(self):
        for (x, y, color) in self.tiles:
            pygame.draw.rect(self.screen, color, (x, y, TILE_SIZE, TILE_SIZE))

        # 마을 건물 표시
        pygame.draw.rect(self.screen, (140, 100, 60), (2 * TILE_SIZE, 2 * TILE_SIZE, 3 * TILE_SIZE, 2 * TILE_SIZE))
        draw_text(self.screen, "상점", 2 * TILE_SIZE + 10, 2 * TILE_SIZE + 14, 22, WHITE)

        # NPC
        pygame.draw.rect(self.screen, (255, 200, 100), (NPC_X, NPC_Y, NPC_SIZE, NPC_SIZE))
        draw_text(self.screen, "상인", NPC_X - 4, NPC_Y - 22, 18, BLACK)

        # 말 걸기 힌트
        if self.talk_hint:
            draw_text(self.screen, "Z: 말 걸기", NPC_X - 10, NPC_Y - 42, 18, YELLOW)

        self.player.draw(self.screen)

        # HUD
        pygame.draw.rect(self.screen, (0, 0, 0), (5, 5, 230, 72))
        draw_text(self.screen, f"Lv.{self.player.level}  HP {self.player.hp}/{self.player.max_hp}", 10, 10, 22, WHITE)
        draw_text(self.screen, f"MP {self.player.mp}/{self.player.max_mp}", 10, 33, 20, (80, 160, 255))
        draw_text(self.screen, f"EXP {self.player.exp}/{self.player.exp_to_next}  Gold {self.player.gold}G", 10, 53, 18, YELLOW)

        # 마을 안내
        if self._in_town():
            draw_text(self.screen, "[ 마을 - 안전지대 ]", 290, 10, 22, YELLOW)
