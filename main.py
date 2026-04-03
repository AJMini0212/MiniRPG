import pygame
import sys
from scenes.world import WorldScene
from scenes.battle import BattleScene
from scenes.shop import ShopScene

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
    shop = None

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
                            world = WorldScene(screen)
                        else:
                            # 전투 승리/도망 시 골드 획득
                            if battle.result == "win":
                                gold = battle.monster.exp // 2
                                world.player.gold += gold
                        current_scene = "world"
                        battle = None

            elif current_scene == "shop":
                result = shop.handle_event(event)
                if result == "exit" or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_x
                ):
                    current_scene = "world"
                    shop = None

        if current_scene == "world":
            world.update()
            world.draw()
            if world.encounter:
                battle = BattleScene(screen, world.player, world.encounter)
                world.encounter = None
                current_scene = "battle"
            elif world.open_shop:
                shop = ShopScene(screen, world.player)
                world.open_shop = False
                current_scene = "shop"

        elif current_scene == "battle":
            battle.draw()

        elif current_scene == "shop":
            shop.draw()

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
