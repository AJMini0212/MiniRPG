import json
import os

SAVE_FILE = "save_data.json"


def save_game(player):
    """플레이어 상태를 저장"""
    data = {
        "x": player.x,
        "y": player.y,
        "hp": player.hp,
        "mp": player.mp,
        "level": player.level,
        "exp": player.exp,
        "gold": player.gold,
        "inventory": player.inventory,
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_game(player):
    """저장된 플레이어 상태를 복원"""
    if not os.path.exists(SAVE_FILE):
        return False
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        player.x = data["x"]
        player.y = data["y"]
        player.hp = data["hp"]
        player.mp = data["mp"]
        player.level = data["level"]
        player.exp = data["exp"]
        player.gold = data["gold"]
        player.inventory = data["inventory"]
        player.rect.topleft = (player.x, player.y)
        return True
    except:
        return False


def has_save():
    """세이브 파일이 존재하는지 확인"""
    return os.path.exists(SAVE_FILE)
