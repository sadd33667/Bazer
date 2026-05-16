# Lab 2 - Cache Implementation

This push contains the first half of Lab 2:

- Three new books were added to the catalog.
- The frontend service now has an in-memory LRU cache for catalog `info` requests.
- Read requests check the cache before calling the catalog service.
- Purchase requests invalidate the cached book entry before the catalog quantity is updated.
- Cache status can be checked through `/cache/stats`.

## Run

```bash
docker compose up --build
```

## Test the cache

First request should come from the catalog service:

```bash
curl http://localhost:5000/info/1
```

Second request should come from the cache:

```bash
curl http://localhost:5000/info/1
```

Check cache statistics:

```bash
curl http://localhost:5000/cache/stats
```

Buy a book, which invalidates its cached entry:

```bash
curl -X POST http://localhost:5000/purchase/1
```

Query the same book again. The response should come from the catalog service because the old cache entry was invalidated:

```bash
curl http://localhost:5000/info/1
```
