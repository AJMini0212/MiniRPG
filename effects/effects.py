import pygame
import random
import math


class Particle:
    """떨어지는 파티클 효과"""
    def __init__(self, x, y, vx, vy, lifetime, color, size=6):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.gravity = 0.2

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime <= 0:
            return
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
        screen.blit(s, (int(self.x) - self.size, int(self.y) - self.size))

    def is_alive(self):
        return self.lifetime > 0


class DamageNumber:
    """데미지 숫자 표시"""
    def __init__(self, x, y, damage, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.lifetime = 60
        self.max_lifetime = 60

    def update(self):
        self.y -= 1
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime <= 0:
            return
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        font = pygame.font.SysFont("malgungothic", 32, bold=True)
        text = font.render(str(self.damage), True, self.color)
        text.set_alpha(alpha)
        screen.blit(text, (int(self.x), int(self.y)))

    def is_alive(self):
        return self.lifetime > 0


class EffectManager:
    """모든 효과 관리"""
    def __init__(self):
        self.particles = []
        self.damage_numbers = []
        self.screen_shake = 0
        self.shake_intensity = 0

    def add_particles(self, x, y, count=10, color=(255, 200, 100), lifetime=40):
        """파티클 생성"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2
            particle = Particle(x, y, vx, vy, lifetime, color)
            self.particles.append(particle)

    def add_damage_number(self, x, y, damage, is_critical=False):
        """데미지 숫자 추가"""
        color = (255, 100, 100) if is_critical else (255, 255, 255)
        self.damage_numbers.append(DamageNumber(x, y, damage, color))

    def shake_screen(self, intensity=5, duration=10):
        """화면 흔들림"""
        self.shake_intensity = intensity
        self.screen_shake = duration

    def capture_effect(self, x, y):
        """포획 효과"""
        self.add_particles(x, y, 20, (255, 220, 100), 50)
        self.shake_screen(8, 15)

    def heal_effect(self, x, y):
        """회복 효과"""
        self.add_particles(x, y, 15, (100, 255, 100), 45)

    def level_up_effect(self, x, y):
        """레벨업 효과"""
        self.add_particles(x, y, 25, (255, 255, 0), 60)
        self.shake_screen(3, 8)

    def update(self):
        """모든 효과 업데이트"""
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()

        self.damage_numbers = [d for d in self.damage_numbers if d.is_alive()]
        for dmg in self.damage_numbers:
            dmg.update()

        if self.screen_shake > 0:
            self.screen_shake -= 1

    def draw(self, screen):
        """모든 효과 그리기"""
        for particle in self.particles:
            particle.draw(screen)
        for dmg in self.damage_numbers:
            dmg.draw(screen)

    def get_screen_shake_offset(self):
        """화면 흔들림 오프셋 반환"""
        if self.screen_shake <= 0:
            return 0, 0
        x = random.randint(-self.shake_intensity, self.shake_intensity)
        y = random.randint(-self.shake_intensity, self.shake_intensity)
        return x, y
