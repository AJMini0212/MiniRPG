from data.monsters import MONSTERS

# 각 지역 정의
REGIONS = {
    "village": {
        "name": "마을",
        "color": (180, 150, 100),
        "dark_color": (160, 130, 80),
        "monsters": [],  # 마을은 안전지대
        "description": "[ 마을 - 안전지대 ]",
    },
    "forest": {
        "name": "초보자 숲",
        "color": (80, 160, 80),
        "dark_color": (60, 120, 60),
        "monsters": ["slime", "bat", "wolf"],
        "description": "[ 초보자 숲 ]",
    },
    "hill": {
        "name": "중급 언덕",
        "color": (150, 140, 80),
        "dark_color": (120, 110, 60),
        "monsters": ["goblin", "wolf", "skeleton"],
        "description": "[ 중급 언덕 ]",
    },
    "cave": {
        "name": "상급 동굴",
        "color": (100, 100, 120),
        "dark_color": (80, 80, 100),
        "monsters": ["skeleton", "orc", "ghost", "golem"],
        "description": "[ 상급 동굴 ]",
    },
    "mountain": {
        "name": "극단 산",
        "color": (180, 100, 100),
        "dark_color": (150, 80, 80),
        "monsters": ["orc", "golem", "ghost", "dragon"],
        "description": "[ 극단 산 ]",
    },
}

# 각 지역의 맵 위치 (타일 단위)
REGION_AREAS = {
    "village": {"x": 10, "y": 7, "w": 8, "h": 6},      # 중앙
    "forest": {"x": 17, "y": 2, "w": 8, "h": 6},       # 우상단
    "hill": {"x": 0, "y": 2, "w": 8, "h": 6},          # 좌상단
    "cave": {"x": 17, "y": 10, "w": 8, "h": 5},        # 우하단
    "mountain": {"x": 0, "y": 10, "w": 8, "h": 5},     # 좌하단
}

# NPC 위치들 (마을에만 있음)
NPC_POSITIONS = [
    {"x": 5 * 32, "y": 4 * 32, "name": "상인"},
    {"x": 7 * 32, "y": 5 * 32, "name": "여행자"},
]
