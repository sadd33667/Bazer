from flask import Flask, jsonify
import requests
from collections import OrderedDict
import os
from itertools import cycle

app = Flask(__name__)
CATALOG_URLS = [
    url.strip()
    for url in os.getenv("CATALOG_URLS", "http://catalog_service_1:5001,http://catalog_service_2:5001").split(",")
    if url.strip()
]
ORDER_URLS = [
    url.strip()
    for url in os.getenv("ORDER_URLS", "http://order_service_1:5002,http://order_service_2:5002").split(",")
    if url.strip()
]
CATEGORY_BALANCER = cycle(CATALOG_URLS)
ORDER_BALANCER = cycle(ORDER_URLS)
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


def next_catalog_url():
    return next(CATEGORY_BALANCER)


def next_order_url():
    return next(ORDER_BALANCER)

@app.route("/")
def home():
    return jsonify({
        "message": "Frontend service is working!",
        "catalog_replicas": CATALOG_URLS,
        "order_replicas": ORDER_URLS
    })


@app.route("/search/<topic>")
def search(topic):
    catalog_url = next_catalog_url()
    response = requests.get(f"{catalog_url}/search/{topic}")
    return jsonify(response.json()), response.status_code


@app.route("/info/<int:item_id>")
def info(item_id):
    cached = get_cached_info(item_id)
    if cached is not None:
        return jsonify({
            "source": "cache",
            "book": cached
        })

    catalog_url = next_catalog_url()
    response = requests.get(f"{catalog_url}/info/{item_id}")
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
    order_url = next_order_url()
    response = requests.post(f"{order_url}/purchase/{item_id}")
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
        "catalog_replicas": CATALOG_URLS,
        "order_replicas": ORDER_URLS,
        **cache_stats
    })


@app.route("/cache/clear", methods=["POST"])
def clear_cache():
    catalog_cache.clear()
    cache_stats.update({"hits": 0, "misses": 0, "invalidations": 0})
    return jsonify({"message": "Cache cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
