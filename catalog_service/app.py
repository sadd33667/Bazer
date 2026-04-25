from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = "catalog.json"

books_data = [
    {
        "id": 1,
        "title": "How to get a good grade in DOS in 40 minutes a day",
        "topic": "distributed systems",
        "quantity": 5,
        "price": 30
    },
    {
        "id": 2,
        "title": "RPCs for Noobs",
        "topic": "distributed systems",
        "quantity": 3,
        "price": 50
    },
    {
        "id": 3,
        "title": "Xen and the Art of Surviving Undergraduate School",
        "topic": "undergraduate school",
        "quantity": 4,
        "price": 40
    },
    {
        "id": 4,
        "title": "Cooking for the Impatient Undergrad",
        "topic": "undergraduate school",
        "quantity": 2,
        "price": 25
    }
]

def load_books():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(books_data, f, indent=4)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_books(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    return jsonify({"message": "Catalog service is working!"})

@app.route("/search/<topic>")
def search(topic):
    books = load_books()
    result = [book for book in books if book["topic"].lower() == topic.lower()]
    return jsonify(result)

@app.route("/info/<int:item_id>")
def info(item_id):
    books = load_books()
    for book in books:
        if book["id"] == item_id:
            return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

@app.route("/update/<int:item_id>", methods=["POST"])
def update(item_id):
    books = load_books()
    data = request.get_json()

    for book in books:
        if book["id"] == item_id:
            if "quantity" in data:
                book["quantity"] = data["quantity"]
            if "price" in data:
                book["price"] = data["price"]

            save_books(books)
            return jsonify({"message": "Book updated successfully"})

    return jsonify({"error": "Book not found"}), 404

if __name__ == "__main__":
    app.run(port=5001, debug=True)