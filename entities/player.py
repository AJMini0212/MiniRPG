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

    def handle_input(self, keys):
        if keys[pygame.K_RIGHT]:
            self.x += SPEED
        if keys[pygame.K_LEFT]:
            self.x -= SPEED
        if keys[pygame.K_DOWN]:
            self.y += SPEED
        if keys[pygame.K_UP]:
            self.y -= SPEED
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.rect(screen, (50, 100, 255), self.rect)

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
