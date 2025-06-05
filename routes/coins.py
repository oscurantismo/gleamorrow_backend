from flask import Blueprint, request, jsonify
from handling.coin_rewards import award_task_completion

coins = Blueprint('coins', __name__)

@coins.route('/api/award-coins', methods=['POST'])
def award_coins():
    data = request.get_json()
    user_id = data.get('user_id')
    task_name = data.get('task_name')
    difficulty = int(data.get('difficulty', 0))

    if not user_id or not task_name:
        return jsonify({'error': 'Missing user_id or task_name'}), 400

    coins_awarded = award_task_completion(user_id, task_name, difficulty)

    return jsonify({'status': 'success', 'coins': coins_awarded})
