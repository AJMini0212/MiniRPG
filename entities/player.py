import pygame
from data.skills import SKILLS
from data.items import DEFAULT_INVENTORY, ITEMS

SPEED = 3
SIZE = 32


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100
        self.max_hp = 100
        self.mp = 30
        self.max_mp = 30
        self.attack = 15
        self.defense = 5
        self.level = 1
        self.exp = 0
        self.exp_to_next = 30
        self.rect = pygame.Rect(x, y, SIZE, SIZE)
        self.skills = SKILLS
        self.inventory = dict(DEFAULT_INVENTORY)
        self.guarding = False
        self.gold = 200
        self.direction = "down"  # up, down, left, right
        self.anim_frame = 0  # 0 또는 1
        self.anim_counter = 0

    def handle_input(self, keys):
        moved = False
        if keys[pygame.K_RIGHT]:
            self.x += SPEED
            self.direction = "right"
            moved = True
        if keys[pygame.K_LEFT]:
            self.x -= SPEED
            self.direction = "left"
            moved = True
        if keys[pygame.K_DOWN]:
            self.y += SPEED
            self.direction = "down"
            moved = True
        if keys[pygame.K_UP]:
            self.y -= SPEED
            self.direction = "up"
            moved = True

        # 애니메이션 업데이트
        if moved:
            self.anim_counter += 1
            if self.anim_counter >= 4:
                self.anim_frame = 1 - self.anim_frame
                self.anim_counter = 0
        else:
            self.anim_frame = 0
            self.anim_counter = 0

        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        base_color = (50, 100, 255)
        accent_color = (100, 180, 255)

        # 애니메이션 오프셋 (이동할 때 위아래로 흔들림)
        bob = 2 if self.anim_frame == 1 else 0

        # 몸통 (직사각형)
        pygame.draw.rect(screen, base_color, (x + 6, y + 12 - bob, 20, 16))

        # 머리 (원형)
        pygame.draw.circle(screen, base_color, (x + 16, y + 8 - bob), 6)

        # 방향에 따른 눈 표시
        eye_color = accent_color
        if self.direction == "up":
            # 위쪽 화살표
            pygame.draw.polygon(screen, eye_color, [(x + 16, y + 2), (x + 14, y + 6), (x + 18, y + 6)])
        elif self.direction == "down":
            # 아래쪽 화살표
            pygame.draw.polygon(screen, eye_color, [(x + 16, y + 14 - bob), (x + 14, y + 10 - bob), (x + 18, y + 10 - bob)])
        elif self.direction == "left":
            # 왼쪽 화살표
            pygame.draw.polygon(screen, eye_color, [(x + 8, y + 8 - bob), (x + 12, y + 6 - bob), (x + 12, y + 10 - bob)])
        elif self.direction == "right":
            # 오른쪽 화살표
            pygame.draw.polygon(screen, eye_color, [(x + 24, y + 8 - bob), (x + 20, y + 6 - bob), (x + 20, y + 10 - bob)])

        # 다리 표시 (애니메이션)
        leg_offset = 3 if self.anim_frame == 1 else -3
        pygame.draw.line(screen, accent_color, (x + 12, y + 28 - bob), (x + 12 + leg_offset, y + 32), 2)
        pygame.draw.line(screen, accent_color, (x + 20, y + 28 - bob), (x + 20 - leg_offset, y + 32), 2)

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_next
        self.exp_to_next = int(self.exp_to_next * 1.5)
        self.max_hp += 10
        self.max_mp += 5
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.attack += 3
        self.defense += 2

    def use_item(self, item_key):
        if self.inventory.get(item_key, 0) <= 0:
            return False, "아이템이 없다!"
        item = ITEMS[item_key]
        self.inventory[item_key] -= 1
        msgs = [f"{item['name']}을(를) 사용했다!"]
        if item["hp"] > 0:
            healed = min(item["hp"], self.max_hp - self.hp)
            self.hp += healed
            msgs.append(f"HP +{healed}")
        if item["mp"] > 0:
            restored = min(item["mp"], self.max_mp - self.mp)
            self.mp += restored
            msgs.append(f"MP +{restored}")
        return True, msgs
