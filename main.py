import pygame
import sys
from scenes.world import WorldScene
from scenes.battle import BattleScene

WIDTH, HEIGHT = 800, 480
FPS = 60


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini RPG")
    clock = pygame.time.Clock()

    world = WorldScene(screen)
    current_scene = "world"
    battle = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if current_scene == "world":
                world.handle_event(event)
            elif current_scene == "battle":
                battle.handle_event(event)
                if battle.result:
                    if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_z):
                        if battle.result == "lose":
                            # 게임 오버 → 재시작
                            world = WorldScene(screen)
                        current_scene = "world"
                        battle = None

        if current_scene == "world":
            world.update()
            world.draw()
            if world.encounter:
                battle = BattleScene(screen, world.player, world.encounter)
                world.encounter = None
                current_scene = "battle"

        elif current_scene == "battle":
            battle.draw()

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
