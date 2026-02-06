# HTTP Metadata Inventory Service

Getting Started
I've containerized everything to make it a "one-command" setup.

Spin it up:

```Bash:
docker-compose up --build
```

The API will be live at http://localhost:8000. You can verify it's healthy by hitting the root endpoint.

# How to use the API
1. (POST /metadata)

It fetches the data and saves it directly to MongoDB.

```Bash:
curl -X POST http://localhost:8000/metadata \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html"}'
```

2. (GET /metadata)

If we have it: You get a 200 OK with the full dataset (headers, cookies, and the page source).

If we don't: The API won't make you wait. 
It returns a 202 Accepted immediately, lets you know the request has been logged, and kicks off an internal background process to fetch it for next time.

```Bash
curl "http://localhost:8000/metadata?url=https://httpbin.org/html"
```

**IMP** You can explore and test all endpoints visually via the Swagger UI at http://localhost:8000/docs.

# The Architecture
I built this following a 3-layer architecture to keep the code clean and maintainable:

Transport Layer (main.py): Handles the FastAPI routes and request validation using Pydantic models.

Logic Layer (collector.py): It handles the actual HTTP metadata collection and error handling.

Data Layer (repository.py & database.py): Manages MongoDB interactions. 

# Testing
The suite is comprehensive, covering unit and integration tests using pytest.

To run them inside the environment:

```Bash:
docker-compose exec api pytest -v
```
