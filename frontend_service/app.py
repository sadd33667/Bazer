from flask import Flask, jsonify
import requests
from collections import OrderedDict

app = Flask(__name__)
CATALOG_URL = "http://catalog_service:5001"
ORDER_URL = "http://order_service:5002"
CACHE_MAX_ITEMS = 5

catalog_cache = OrderedDict()
cache_stats = {
    "hits": 0,
    "misses": 0,
    "invalidations": 0
}


def get_cached_info(item_id):
    cached = catalog_cache.get(item_id)
    if cached is None:
        cache_stats["misses"] += 1
        return None

    cache_stats["hits"] += 1
    catalog_cache.move_to_end(item_id)
    return cached


def put_cached_info(item_id, book_info):
    catalog_cache[item_id] = book_info
    catalog_cache.move_to_end(item_id)

    if len(catalog_cache) > CACHE_MAX_ITEMS:
        catalog_cache.popitem(last=False)


def invalidate_cached_info(item_id):
    removed = catalog_cache.pop(item_id, None)
    if removed is not None:
        cache_stats["invalidations"] += 1

@app.route("/")
def home():
    return jsonify({"message": "Frontend service is working!"})


@app.route("/search/<topic>")
def search(topic):
    response = requests.get(f"{CATALOG_URL}/search/{topic}")
    return jsonify(response.json()), response.status_code


@app.route("/info/<int:item_id>")
def info(item_id):
    cached = get_cached_info(item_id)
    if cached is not None:
        return jsonify({
            "source": "cache",
            "book": cached
        })

    response = requests.get(f"{CATALOG_URL}/info/{item_id}")
    data = response.json()

    if response.status_code == 200:
        put_cached_info(item_id, data)

    return jsonify({
        "source": "catalog_service",
        "book": data
    }), response.status_code


@app.route("/purchase/<int:item_id>", methods=["GET", "POST"])
def purchase(item_id):
    invalidate_cached_info(item_id)
    response = requests.post(f"{ORDER_URL}/purchase/{item_id}")
    return jsonify(response.json()), response.status_code


@app.route("/cache/invalidate/<int:item_id>", methods=["POST"])
def invalidate(item_id):
    invalidate_cached_info(item_id)
    return jsonify({"message": "Cache entry invalidated", "item_id": item_id})


@app.route("/cache/stats")
def stats():
    return jsonify({
        "items": list(catalog_cache.keys()),
        "size": len(catalog_cache),
        "max_size": CACHE_MAX_ITEMS,
        **cache_stats
    })


@app.route("/cache/clear", methods=["POST"])
def clear_cache():
    catalog_cache.clear()
    cache_stats.update({"hits": 0, "misses": 0, "invalidations": 0})
    return jsonify({"message": "Cache cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
