from flask import Flask, jsonify
import requests
import json
import os
from itertools import cycle

app = Flask(__name__)

ORDERS_FILE = os.getenv("ORDERS_FILE", "orders.json")
SERVICE_NAME = os.getenv("SERVICE_NAME", "order_service")
CATALOG_URLS = [
    url.strip()
    for url in os.getenv("CATALOG_URLS", "http://catalog_service_1:5001,http://catalog_service_2:5001").split(",")
    if url.strip()
]
CATALOG_BALANCER = cycle(CATALOG_URLS)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://frontend_service:5000")


def next_catalog_url():
    return next(CATALOG_BALANCER)


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
    return jsonify({
        "message": "Order service is working!",
        "service": SERVICE_NAME,
        "catalog_replicas": CATALOG_URLS
    })


@app.route("/purchase/<int:item_id>", methods=["POST", "GET"])
def purchase(item_id):
    try:
        requests.post(f"{FRONTEND_URL}/cache/invalidate/{item_id}", timeout=2)
    except requests.RequestException:
        print(f"Could not invalidate frontend cache for item {item_id}")

    catalog_url = next_catalog_url()
    info_response = requests.get(f"{catalog_url}/info/{item_id}")

    if info_response.status_code != 200:
        return jsonify({"error": "Book not found in catalog"}), 404

    book = info_response.json()

    if book["quantity"] <= 0:
        return jsonify({"message": "Out of stock"}), 400

    new_quantity = book["quantity"] - 1

    update_response = requests.post(
        f"{catalog_url}/update/{item_id}",
        json={"quantity": new_quantity, "replicate": True}
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
        "remaining_quantity": new_quantity,
        "served_by": SERVICE_NAME
    })


if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5002, debug=True)
