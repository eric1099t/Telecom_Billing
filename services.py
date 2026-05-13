from database import BillingDB
from models import CDRRequest

class BillingService:
    def __init__(self, db: BillingDB):
        self.db = db
        self.PRICE_PER_MINUTE = 1000  # Example price per minute
        
    def process_call_billing(self, cdr: CDRRequest) -> dict:
        if cdr.duration_seconds <= 0:
            return ValueError(f"Invalid call duration: {cdr.duration_seconds}. Must be greater than 0.")

        phone = cdr.phone_number
        user_info = self.db.get_user(phone)
        if not user_info:
            return ValueError(f"Subscriber with phone number {phone} not found.")
        
        if user_info['status'] != 'ACTIVE':
            return {"status": "REJECTED", "reason": f"Subscriber status is {user_info['status']}. Call rejected."}
        
        # Calculate call cost based on duration and price per minute
        cost = round((cdr.duration_seconds / 60) * self.PRICE_PER_MINUTE, 2)
        
        # Get current balance and debt limit to check if the call can be accepted
        current_balance = float(self.db.get_balance(phone) or 0)
        
        # Get debt limit; if not set, default to 0 (no debt allowed)
        limit = float(user_info.get('debt_limit', 0))
        
        if (current_balance - cost) < -limit:
            return {"status": "REJECTED", "reason": f"Insufficient balance. Call cost: {cost}, Current balance: {current_balance}, Debt limit: {limit}.", "cost_required": cost}
        
        # Deduct the cost from the user's balance in Redis
        new_balance = self.db.deduct_balance(phone, cost)
        return {"status": "ACCEPTED", "phone": phone, "plan": user_info.get('plan'), "cost": cost, "remaining_balance": round(new_balance, 2)}