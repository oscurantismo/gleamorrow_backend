# coin_rewards.py
from routes.reward_logger import log_coin_reward

DIFFICULTY_COINS = {
    1: 10,
    2: 15,
    3: 25,
    4: 40,
}

def award_task_completion(user_id, task_name, difficulty):
    coins = DIFFICULTY_COINS.get(difficulty, 0)
    log_coin_reward(user_id, task_name, difficulty, coins)
    return coins
