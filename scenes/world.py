import pygame
import random
from entities.player import Player
from data.monsters import MONSTERS
from data.regions import REGIONS, REGION_AREAS, NPC_POSITIONS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 0)
GRAY = (180, 180, 180)

TILE_SIZE = 32
ENCOUNTER_CHANCE = 0.004

# 맵 크기 (타일 단위)
MAP_COLS = 25
MAP_ROWS = 15
MAP_W = MAP_COLS * TILE_SIZE
MAP_H = MAP_ROWS * TILE_SIZE

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
        self.current_region = self._get_region_at(self.player.x // TILE_SIZE, self.player.y // TILE_SIZE)
        self._build_map()

    def _get_region_at(self, col, row):
        """좌표에 해당하는 지역 반환"""
        for region_key, area in REGION_AREAS.items():
            if area["x"] <= col < area["x"] + area["w"] and area["y"] <= row < area["y"] + area["h"]:
                return region_key
        return "village"  # 기본값

    def _build_map(self):
        self.tiles = []
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                region_key = self._get_region_at(c, r)
                region = REGIONS[region_key]
                color = region["color"] if (r + c) % 2 == 0 else region["dark_color"]
                self.tiles.append((c * TILE_SIZE, r * TILE_SIZE, color))

    def _in_region(self, region_key):
        px, py = self.player.x // TILE_SIZE, self.player.y // TILE_SIZE
        area = REGION_AREAS[region_key]
        return area["x"] <= px < area["x"] + area["w"] and area["y"] <= py < area["y"] + area["h"]

    def _near_npc(self):
        if self.current_region != "village":
            return False
        for npc in NPC_POSITIONS:
            dx = self.player.x - npc["x"]
            dy = self.player.y - npc["y"]
            if (dx * dx + dy * dy) ** 0.5 < TALK_RANGE:
                return True
        return False

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

        # 현재 지역 업데이트
        self.current_region = self._get_region_at(self.player.x // TILE_SIZE, self.player.y // TILE_SIZE)

        self.talk_hint = self._near_npc()

        moving = any([
            keys[pygame.K_UP], keys[pygame.K_DOWN],
            keys[pygame.K_LEFT], keys[pygame.K_RIGHT],
        ])

        # 현재 지역의 몬스터 가져오기
        monsters = REGIONS[self.current_region]["monsters"]

        # 지역에 몬스터가 있고 이동 중일 때만 인카운터 가능
        if moving and monsters and random.random() < ENCOUNTER_CHANCE:
            monster_key = random.choice(monsters)
            self.encounter = MONSTERS[monster_key]

    def draw(self):
        # 타일 그리기
        for (x, y, color) in self.tiles:
            pygame.draw.rect(self.screen, color, (x, y, TILE_SIZE, TILE_SIZE))

        # 마을 건물 (마을 지역에만)
        if self._in_region("village"):
            village_area = REGION_AREAS["village"]
            building_x = (village_area["x"] + 2) * TILE_SIZE
            building_y = village_area["y"] * TILE_SIZE
            pygame.draw.rect(self.screen, (140, 100, 60), (building_x, building_y, 3 * TILE_SIZE, 2 * TILE_SIZE))
            draw_text(self.screen, "상점", building_x + 10, building_y + 14, 22, WHITE)

        # NPC 그리기 (마을에만)
        if self._in_region("village"):
            for npc in NPC_POSITIONS:
                pygame.draw.rect(self.screen, (255, 200, 100), (npc["x"], npc["y"], NPC_SIZE, NPC_SIZE))
                draw_text(self.screen, npc["name"], npc["x"] - 10, npc["y"] - 22, 18, BLACK)

        # 말 걸기 힌트
        if self.talk_hint:
            draw_text(self.screen, "Z: 말 걸기", self.player.x - 10, self.player.y - 42, 18, YELLOW)

        # 플레이어 그리기
        self.player.draw(self.screen)

        # HUD - 플레이어 정보 패널 (좌상단)
        pygame.draw.rect(self.screen, (45, 45, 60), (5, 5, 250, 85))
        pygame.draw.rect(self.screen, (100, 100, 120), (5, 5, 250, 85), 2)

        draw_text(self.screen, f"Lv. {self.player.level}", 15, 10, 18, YELLOW)
        draw_text(self.screen, f"HP {self.player.hp}/{self.player.max_hp}", 15, 35, 18, WHITE)
        draw_text(self.screen, f"MP {self.player.mp}/{self.player.max_mp}", 15, 55, 16, (100, 180, 255))
        draw_text(self.screen, f"Gold {self.player.gold}G", 130, 10, 16, YELLOW)

        # 팀 상태 표시
        draw_text(self.screen, f"팀: {len([m for m in self.player.team if m.hp > 0])}/{len(self.player.team)}", 130, 32, 14, WHITE)
        for i, m in enumerate(self.player.team[:3]):
            x = 130 + (i % 3) * 30
            y = 50 + (i // 3) * 12
            bar_color = (50, 200, 50) if m.hp > 0 else (200, 50, 50)
            pygame.draw.rect(self.screen, (60, 60, 60), (x, y, 25, 8))
            hp_ratio = max(0, min(1, m.hp / m.max_hp)) if m.max_hp > 0 else 0
            pygame.draw.rect(self.screen, bar_color, (x, y, int(25 * hp_ratio), 8))

        # 지역 정보 패널 (우상단)
        region = REGIONS[self.current_region]
        region_info = region["description"]
        pygame.draw.rect(self.screen, (45, 45, 60), (540, 5, 255, 85))
        pygame.draw.rect(self.screen, (100, 100, 120), (540, 5, 255, 85), 2)
        draw_text(self.screen, region_info, 555, 15, 20, YELLOW)

        if self.current_region == "village":
            draw_text(self.screen, "안전지대 - 몬스터 없음", 555, 45, 16, WHITE)
        else:
            difficulty = ['약', '중', '강', '극강'][['forest', 'hill', 'cave', 'mountain'].index(self.current_region)]
            draw_text(self.screen, f"난이도: {difficulty}", 555, 45, 16, WHITE)

        draw_text(self.screen, "방향키: 이동  Z: 상호작용", 555, 65, 14, GRAY)
