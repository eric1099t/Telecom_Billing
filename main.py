from fastapi import FastAPI, HTTPException
from database import BillingDB
from services import BillingService
from models import CDRRequest, SubscriberPayload

app = FastAPI(title="Telecom Billing API")

db = BillingDB(json_path="subscribers.json")
billing_service = BillingService(db)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Telecom Billing API!"}

# Load subscribers from JSON to Redis on startup and save back on shutdown
@app.on_event("startup")
def startup():
    count = db.load_to_redis()
    print(f"Loaded {count} subscribers into Redis.")

# Save to JSON on shutdown to persist any changes made during runtime  
@app.on_event("shutdown")
def shutdown():
    db.save_to_json()
    print("Saved subscribers to JSON.")

# API Endpoints
# Get balance for a subscriber``
@app.get("/balance/{phone}")
def get_balance(phone: str):
    balance = db.get_balance(phone)
    if balance is None:
        raise HTTPException(status_code=404, detail=f"Subscriber with phone number {phone} not found.")
    return {"phone": phone, "balance": float(balance)}

# Get subscriber details
@app.get("/subscriber/{phone}")
def get_subscriber(phone: str):
    user_info = db.get_user(phone)
    if not user_info:
        raise HTTPException(status_code=404, detail=f"Subscriber with phone number {phone} not found.")
    balance = db.get_balance(phone)
    user_info['balance'] = float(balance) if balance is not None else 0.0
    user_info['phone_number'] = phone
    return user_info

# Get all subscribers
@app.get("/subscribers")
def get_all_subscribers():
    subscribers = db.get_all_subscribers()
    return {"message": f"Retrieved {len(subscribers)} subscribers.", "total_count": len(subscribers), "data": subscribers}

# Process call billing based on CDR input
@app.post("/call/process")
def process_call(payload: CDRRequest):
    try:
        result = billing_service.process_call_billing(payload)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Create a new subscriber    
@app.post("/subscriber")
def create_subscriber(payload: SubscriberPayload):
    phone = payload.phone_number
    if db.get_user(phone):
        raise HTTPException(status_code=400, detail=f"Subscriber with phone number {phone} already exists.")
    
    user_date = {
        "name": payload.name,
        "status": payload.status.value,
        "plan": payload.plan.value,
        "debt_limit": payload.debt_limit
    }
    
    db.save_subscriber(phone, user_date, payload.balance)
    db.save_to_json()  # Save to JSON to persist changes
    return {"message": f"Subscriber with phone number {phone} created successfully.", "data": payload.dict()}

# Update an existing subscriber's details and balance
@app.put("/subscriber/{phone}")
def update_subscriber(phone: str, payload: SubscriberPayload):
    if not db.get_user(phone):
        raise HTTPException(status_code=404, detail=f"Subscriber with phone number {phone} not found.")
    
    user_date = {
        "name": payload.name,
        "status": payload.status.value,
        "plan": payload.plan.value,
        "debt_limit": payload.debt_limit
    }
    
    db.save_subscriber(phone, user_date, payload.balance)
    db.save_to_json()  # Save to JSON to persist changes
    return {"message": f"Subscriber with phone number {phone} updated successfully.", "data": payload.dict()}

# Delete a subscriber
@app.delete("/subscriber/{phone}")
def delete_subscriber(phone: str):
    if not db.get_user(phone):
        raise HTTPException(status_code=404, detail=f"Subscriber with phone number {phone} not found.")
    db.delete_subscriber(phone)
    return {"message": f"Subscriber with phone number {phone} deleted successfully."}
