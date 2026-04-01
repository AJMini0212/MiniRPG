import pygame
import random
from entities.player import Player
from data.monsters import MONSTERS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 0)

TILE_SIZE = 32
GRASS_COLOR = (80, 160, 80)
DARK_GRASS_COLOR = (60, 120, 60)
ENCOUNTER_CHANCE = 0.004  # 매 프레임 인카운터 확률


def draw_text(screen, text, x, y, size=22, color=BLACK):
    font = pygame.font.SysFont("malgungothic", size)
    screen.blit(font.render(text, True, color), (x, y))


class WorldScene:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player(384, 224)
        self.encounter = None  # 인카운터 발생 시 monster_data 저장
        self._build_map()

    def _build_map(self):
        cols = 800 // TILE_SIZE + 1
        rows = 480 // TILE_SIZE + 1
        self.tiles = []
        for r in range(rows):
            for c in range(cols):
                color = GRASS_COLOR if (r + c) % 2 == 0 else DARK_GRASS_COLOR
                self.tiles.append((c * TILE_SIZE, r * TILE_SIZE, color))

    def handle_event(self, event):
        pass

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        moving = any([
            keys[pygame.K_UP], keys[pygame.K_DOWN],
            keys[pygame.K_LEFT], keys[pygame.K_RIGHT],
        ])
        if moving and random.random() < ENCOUNTER_CHANCE:
            self.encounter = random.choice(list(MONSTERS.values()))

    def draw(self):
        for (x, y, color) in self.tiles:
            pygame.draw.rect(self.screen, color, (x, y, TILE_SIZE, TILE_SIZE))

        self.player.draw(self.screen)

        # HUD
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (5, 5, 180, 60))
        draw_text(self.screen, f"Lv.{self.player.level}  HP {self.player.hp}/{self.player.max_hp}", 10, 10, 22, WHITE)
        draw_text(self.screen, f"EXP {self.player.exp}/{self.player.exp_to_next}", 10, 35, 20, YELLOW)
