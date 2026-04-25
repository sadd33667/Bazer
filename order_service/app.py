from flask import Flask, jsonify
import requests
import json
import os

app = Flask(__name__)

ORDERS_FILE = "orders.json"
CATALOG_URL = "http://127.0.0.1:5001"


def load_orders():
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "w") as f:
            json.dump([], f, indent=4)

    with open(ORDERS_FILE, "r") as f:
        return json.load(f)


def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def home():
    return jsonify({"message": "Order service is working!"})


@app.route("/purchase/<int:item_id>", methods=["POST", "GET"])
def purchase(item_id):
    info_response = requests.get(f"{CATALOG_URL}/info/{item_id}")

    if info_response.status_code != 200:
        return jsonify({"error": "Book not found in catalog"}), 404

    book = info_response.json()

    if book["quantity"] <= 0:
        return jsonify({"message": "Out of stock"}), 400

    new_quantity = book["quantity"] - 1

    update_response = requests.post(
        f"{CATALOG_URL}/update/{item_id}",
        json={"quantity": new_quantity}
    )

    if update_response.status_code != 200:
        return jsonify({"error": "Failed to update catalog"}), 500

    orders = load_orders()
    orders.append({
        "item_id": item_id,
        "title": book["title"]
    })
    save_orders(orders)

    print(f'bought book "{book["title"]}"')

    return jsonify({
        "message": "Purchase successful",
        "book": book["title"],
        "remaining_quantity": new_quantity
    })


if __name__ == "__main__":
    app.run(port=5002, debug=True)