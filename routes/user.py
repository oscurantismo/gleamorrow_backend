from flask import Blueprint, request, jsonify
from handling.coin_rewards import get_user_coins

user = Blueprint("user", __name__)

@user.route("/api/user-coins", methods=["GET"])
def fetch_user_coins():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400
    coins = get_user_coins(user_id)
    return jsonify({"coins": coins})
