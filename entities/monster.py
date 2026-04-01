import pygame
import copy


class Monster:
    def __init__(self, data):
        d = copy.deepcopy(data)
        self.name = d["name"]
        self.max_hp = d["hp"]
        self.hp = d["hp"]
        self.attack = d["attack"]
        self.defense = d["defense"]
        self.exp = d["exp"]
        self.color = d["color"]

    def is_alive(self):
        return self.hp > 0
