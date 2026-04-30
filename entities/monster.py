import pygame
import copy


class Monster:
    def __init__(self, data, level=1):
        d = copy.deepcopy(data)
        self.name = d["name"]
        self.level = level
        self.base_hp = d["hp"]
        self.base_attack = d["attack"]
        self.base_defense = d["defense"]
        self.exp_reward = d["exp"]
        self.color = d["color"]

        # 레벨에 따른 능력치 계산
        self.max_hp = int(self.base_hp * (1 + (level - 1) * 0.1))
        self.hp = self.max_hp
        self.attack = int(self.base_attack * (1 + (level - 1) * 0.08))
        self.defense = int(self.base_defense * (1 + (level - 1) * 0.05))
        self.exp = 0
        self.exp_to_level = 30

    def is_alive(self):
        return self.hp > 0

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_level
        self.exp_to_level = int(self.exp_to_level * 1.2)

        # 능력치 증가
        self.base_hp = int(self.base_hp * 1.1)
        self.base_attack = int(self.base_attack * 1.08)
        self.base_defense = int(self.base_defense * 1.05)

        self.max_hp = int(self.base_hp * (1 + (self.level - 1) * 0.1))
        self.hp = self.max_hp
        self.attack = int(self.base_attack * (1 + (self.level - 1) * 0.08))
        self.defense = int(self.base_defense * (1 + (self.level - 1) * 0.05))
