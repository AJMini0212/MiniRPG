import pygame
import sys
from scenes.menu import MenuScene
from scenes.world import WorldScene
from scenes.battle import BattleScene
from scenes.shop import ShopScene
from data.save_system import save_game, load_game

WIDTH, HEIGHT = 800, 480
FPS = 60


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini RPG")
    clock = pygame.time.Clock()

    current_scene = "menu"
    menu = MenuScene(screen)
    world = None
    battle = None
    shop = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if current_scene == "menu":
                menu.handle_event(event)

            elif current_scene == "world":
                result = world.handle_event(event)
                if result == "menu":
                    save_game(world.player)
                    current_scene = "menu"
                    menu = MenuScene(screen)

            elif current_scene == "battle":
                battle.handle_event(event)
                if battle.result:
                    if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_z):
                        if battle.result == "lose":
                            save_game(world.player)
                            current_scene = "menu"
                            menu = MenuScene(screen)
                        else:
                            if battle.result == "win":
                                gold = battle.monster.exp // 2
                                world.player.gold += gold
                        if current_scene != "menu":
                            current_scene = "world"
                            battle = None

            elif current_scene == "shop":
                result = shop.handle_event(event)
                if result == "exit" or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_x
                ):
                    current_scene = "world"
                    shop = None

        # 메뉴
        if current_scene == "menu":
            if menu.choice:
                if menu.choice == "new_game":
                    world = WorldScene(screen)
                    current_scene = "world"
                    menu.choice = None
                elif menu.choice == "load_game":
                    world = WorldScene(screen)
                    if load_game(world.player):
                        current_scene = "world"
                    else:
                        menu.choice = None
                elif menu.choice == "quit":
                    pygame.quit()
                    sys.exit()
            menu.draw()

        # 게임 월드
        elif current_scene == "world":
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

        # 전투
        elif current_scene == "battle":
            battle.draw()

        # 상점
        elif current_scene == "shop":
            shop.draw()

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
