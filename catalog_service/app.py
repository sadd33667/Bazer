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
    },
    {
        "id": 5,
        "title": "How to finish Project 3 on time",
        "topic": "distributed systems",
        "quantity": 8,
        "price": 45
    },
    {
        "id": 6,
        "title": "Why theory classes are so hard.",
        "topic": "distributed systems",
        "quantity": 6,
        "price": 35
    },
    {
        "id": 7,
        "title": "Spring in the Pioneer Valley",
        "topic": "undergraduate school",
        "quantity": 5,
        "price": 25
    }
]

def load_books():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(books_data, f, indent=4)
    with open(DATA_FILE, "r") as f:
        books = json.load(f)

    existing_ids = {book["id"] for book in books}
    missing_books = [book for book in books_data if book["id"] not in existing_ids]
    if missing_books:
        books.extend(missing_books)
        save_books(books)

    return books

def save_books(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    return jsonify({"message": "Catalog service is working!"})

@app.route("/search/<topic>")
def search(topic):
    books = load_books()
    result = [
        {"id": book["id"], "title": book["title"]}
        for book in books if book["topic"].lower() == topic.lower()
    ]
    return jsonify(result)

@app.route("/info/<int:item_id>")
def info(item_id):
    books = load_books()
    for book in books:
        if book["id"] == item_id:
            return jsonify({
                "title": book["title"],
                "quantity": book["quantity"],
                "price": book["price"]
            })
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
    app.run(host="0.0.0.0", port=5001, debug=True)
