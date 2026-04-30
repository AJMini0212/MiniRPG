import json
import os

SAVE_FILE = "save_data.json"


def save_game(player):
    """플레이어 상태를 저장"""
    # 팀 몬스터 저장
    team_data = []
    for monster in player.team:
        team_data.append({
            "name": monster.name,
            "level": monster.level,
            "exp": monster.exp,
            "hp": monster.hp,
            "max_hp": monster.max_hp,
        })

    data = {
        "x": player.x,
        "y": player.y,
        "hp": player.hp,
        "mp": player.mp,
        "level": player.level,
        "exp": player.exp,
        "gold": player.gold,
        "inventory": player.inventory,
        "team": team_data,
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_game(player):
    """저장된 플레이어 상태를 복원"""
    if not os.path.exists(SAVE_FILE):
        return False
    try:
        from entities.monster import Monster

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

        # 팀 복원
        player.team = []
        for team_data in data.get("team", []):
            # 더미 데이터로 Monster 생성
            dummy_data = {
                "name": team_data["name"],
                "hp": team_data["hp"],
                "attack": 10,
                "defense": 5,
                "exp": 10,
                "color": (100, 100, 100),
            }
            monster = Monster(dummy_data, team_data["level"])
            monster.hp = team_data["hp"]
            monster.max_hp = team_data["max_hp"]
            monster.exp = team_data["exp"]
            player.team.append(monster)

        return True
    except:
        return False


def has_save():
    """세이브 파일이 존재하는지 확인"""
    return os.path.exists(SAVE_FILE)
