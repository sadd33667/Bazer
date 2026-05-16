# Lab 2 - Replication, Load Balancing, and Measurements

This push completes the second half of Lab 2:

- The catalog service now runs as two replicas: `catalog_service_1` and `catalog_service_2`.
- The order service now runs as two replicas: `order_service_1` and `order_service_2`.
- The frontend uses round-robin load balancing across catalog replicas for search/info requests.
- The frontend uses round-robin load balancing across order replicas for purchase requests.
- Catalog writes are replicated to the peer catalog replica so quantities remain synchronized.
- A small performance script is included in `docs/performance_test.py`.

## Run

```bash
docker compose up --build
```

## Check Replicas

Frontend:

```bash
curl http://localhost:5000/
```

Catalog replica 1:

```bash
curl http://localhost:5001/info/1
```

Catalog replica 2:

```bash
curl http://localhost:5003/info/1
```

Order replica 1:

```bash
curl http://localhost:5002/ 
```

Order replica 2:

```bash
curl http://localhost:5004/
```

## Test Load Balancing

Run this several times:

```bash
curl http://localhost:5000/info/1
```

When the response is not served from cache, the `served_by` value inside `book` alternates between catalog replicas.

Clear the cache when you want to force catalog requests:

```bash
curl -X POST http://localhost:5000/cache/clear
```

Run purchases several times:

```bash
curl -X POST http://localhost:5000/purchase/1
```

The `served_by` value alternates between order replicas.

## Test Catalog Replication

Buy a book through the frontend:

```bash
curl -X POST http://localhost:5000/purchase/1
```

Then check both catalog replicas:

```bash
curl http://localhost:5001/info/1
curl http://localhost:5003/info/1
```

Both replicas should show the same remaining quantity.

## Performance Measurements

With the system running, install/use Python requests if needed, then run:

```bash
python docs/performance_test.py
```

Copy the printed Markdown table into the final report.
