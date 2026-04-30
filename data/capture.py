import random


def calculate_catch_rate(enemy_hp, enemy_max_hp, enemy_level):
    """
    포획 확률 계산
    - HP가 낮을수록 높음
    - 레벨이 낮을수록 높음
    """
    hp_ratio = enemy_hp / enemy_max_hp  # 0~1
    base_rate = 0.4  # 기본 40%

    # HP가 낮을수록 확률 증가
    hp_bonus = (1 - hp_ratio) * 0.4  # 0~40% 추가

    # 레벨에 따른 페널티
    level_penalty = max(0, (enemy_level - 1) * 0.05)  # 레벨당 5% 감소

    catch_rate = base_rate + hp_bonus - level_penalty
    return max(0.1, min(1.0, catch_rate))  # 10~100% 범위


def attempt_catch(enemy_monster):
    """포획 시도"""
    catch_rate = calculate_catch_rate(enemy_monster.hp, enemy_monster.max_hp, enemy_monster.level)
    return random.random() < catch_rate, catch_rate
