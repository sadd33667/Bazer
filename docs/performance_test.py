import statistics
import time

import requests


BASE_URL = "http://localhost:5000"
REQUESTS_PER_TEST = 20


def timed_request(method, path):
    start = time.perf_counter()
    response = requests.request(method, f"{BASE_URL}{path}")
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.raise_for_status()
    return elapsed_ms, response.json()


def run_query_test(label, clear_cache):
    if clear_cache:
        requests.post(f"{BASE_URL}/cache/clear").raise_for_status()

    timings = []
    for _ in range(REQUESTS_PER_TEST):
        elapsed_ms, _ = timed_request("GET", "/info/1")
        timings.append(elapsed_ms)

    return {
        "test": label,
        "requests": REQUESTS_PER_TEST,
        "average_ms": round(statistics.mean(timings), 2),
        "min_ms": round(min(timings), 2),
        "max_ms": round(max(timings), 2),
    }


def run_purchase_test():
    requests.post(f"{BASE_URL}/cache/clear").raise_for_status()
    timed_request("GET", "/info/2")

    purchase_ms, purchase_body = timed_request("POST", "/purchase/2")
    miss_ms, miss_body = timed_request("GET", "/info/2")

    return {
        "test": "cache invalidation after purchase",
        "purchase_ms": round(purchase_ms, 2),
        "next_query_ms": round(miss_ms, 2),
        "purchase_served_by": purchase_body.get("served_by"),
        "next_query_source": miss_body.get("source"),
    }


def main():
    results = [
        run_query_test("first query after cache clear", clear_cache=True),
        run_query_test("repeated cached queries", clear_cache=False),
        run_purchase_test(),
    ]

    print("| Test | Requests | Avg ms | Min ms | Max ms | Notes |")
    print("| --- | ---: | ---: | ---: | ---: | --- |")
    for result in results:
        if result["test"] == "cache invalidation after purchase":
            print(
                f"| {result['test']} | 2 | {result['purchase_ms']} | "
                f"{result['next_query_ms']} | {result['next_query_ms']} | "
                f"purchase by {result['purchase_served_by']}, next query from {result['next_query_source']} |"
            )
        else:
            print(
                f"| {result['test']} | {result['requests']} | {result['average_ms']} | "
                f"{result['min_ms']} | {result['max_ms']} | |"
            )


if __name__ == "__main__":
    main()
