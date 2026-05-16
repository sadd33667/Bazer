from flask import Flask, jsonify
import requests

app = Flask(__name__)
CATALOG_URL = "http://catalog_service:5001"
ORDER_URL = "http://order_service:5002"

@app.route("/")
def home():
    return jsonify({"message": "Frontend service is working!"})


@app.route("/search/<topic>")
def search(topic):
    response = requests.get(f"{CATALOG_URL}/search/{topic}")
    return jsonify(response.json()), response.status_code


@app.route("/info/<int:item_id>")
def info(item_id):
    response = requests.get(f"{CATALOG_URL}/info/{item_id}")
    return jsonify(response.json()), response.status_code


@app.route("/purchase/<int:item_id>", methods=["GET", "POST"])
def purchase(item_id):
    response = requests.post(f"{ORDER_URL}/purchase/{item_id}")
    return jsonify(response.json()), response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
