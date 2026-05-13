### Telecom Billing API 📡

A high-performance, RESTful Billing System built with FastAPI, Redis, and Python. This project demonstrates advanced backend concepts including real-time data processing, dual-layer storage (In-memory & Persistent), and modular architecture.

## 🌟 Features

- **Full CRUD Operations**: Efficiently manage subscriber profiles (Create, Read, Update, Delete).

- **Real-time CDR Processing**: Process Call Detail Records (CDR) and calculate billing costs instantly.

- **Dual-layer Storage**: Uses Redis for ultra-fast arithmetic operations (balance updates) and JSON for persistent state across restarts.

- **Business Logic Validation**: Ensures call rejection based on account status, balance limits, or debt thresholds.

- **Modular Architecture**: Clean separation between API routing, business logic, and data access layers.

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Framework**: FastAPI
- **Database** Redis (In-memory)
- **Persistence**: JSON File
- **Validation**: Pydantic

## 📂 Project Structure
- `main.py`: The entry point of the application. Handles API routing and request/response lifecycle (The Controller).
- `services.py`: Contains the core billing logic, price calculations, and business rule enforcement (The Service Layer).
- `database.py`: Manages interactions with Redis and handles synchronization with subscribers.json (The Data Access Layer).
- `models.py`: Defines Pydantic schemas for request validation and data structure.
- `subscribers.json`: The local persistent storage for subscriber data.

## 🚀 Getting Started

### Prerequisites
Ensure you have Python and a Redis server (or Docker) running. Install the required libraries:

```bash
pip install fastapi uvicorn pydantic redis
```

Running the server:

```bash
python -m uvicorn main:app --reload
```

## 📡 API Endpoints

Interactive Swagger UI is available at http://127.0.0.1:8000/docs

---

### 1. Subscriber Management (GET, POST, PUT, DELETE)

-   **Retrieve all subscribers (GET):**
    ```bash
    curl http://127.0.0.1:8000/subscribers
    ```

-   **Create a new subscriber (POST):**
    ```bash
    curl -X POST http://127.0.0.1:8000/subscriber \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "0988888888", "name": "Eric", "balance": 50000, "status": "ACTIVE", "plan": "PREPAID", "debt_limit": 0}'
     ```

-   **Update an existing subscriber's status (PUT):**
    ```bash
    curl -X PUT http://127.0.0.1:8000/subscriber/0988888888 \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "0988888888", "name": "Eric New", "balance": 100000, "status": "ACTIVE", "plan": "POSTPAID", "debt_limit": -50000}'
    ```

-   **Delete a subscriber (DELETE):**
    ```bash
    curl -X DELETE http://127.0.0.1:8000/subscriber/0988888888
    ```

### 2. Billing & Call Processing

-   **Process a Call (POST):**
    Calculates cost based on duration and updates the subscriber's balance in Redis.

    ```bash
    curl -X POST http://127.0.0.1:8000/call/process \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "0988888888", "duration_seconds": 120, "call_type": "INTERNAL"}'
    ```