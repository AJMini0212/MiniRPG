import pygame

SPEED = 3
SIZE = 32


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100
        self.max_hp = 100
        self.attack = 15
        self.defense = 5
        self.level = 1
        self.exp = 0
        self.exp_to_next = 30
        self.rect = pygame.Rect(x, y, SIZE, SIZE)

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
        self.hp = self.max_hp
        self.attack += 3
        self.defense += 2
