from flask import request, jsonify
from handling.user_coins import get_user_coins

@app.route("/api/user-coins", methods=["GET"])
def fetch_user_coins():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400
    coins = get_user_coins(user_id)
    return jsonify({"coins": coins})
