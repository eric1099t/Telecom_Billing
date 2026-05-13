from pydantic import BaseModel
from enum import Enum

class SubscriberStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEACTIVE = "DEACTIVE"
    SUSPENDED = "SUSPENDED"
    
class BillingPlan(str, Enum):
    PREPAID = "PREPAID"
    POSTPAID = "POSTPAID"
    
class CDRRequest(BaseModel):
    phone_number: str
    duration_seconds: int
    call_type: str = "INTERNAL"
    
class Subscriber:
    def __init__(self, phone_number: str, name: str, balance: float, status: SubscriberStatus=SubscriberStatus.ACTIVE, plan: BillingPlan=BillingPlan.PREPAID, debt_limit: float = 0.0):
        self.phone_number = phone_number
        self.name = name
        self.balance = balance
        self.status = status
        self.plan = plan
        self.debt_limit = debt_limit

    def to_dict(self):
        return {
            "phone_number": self.phone_number,
            "name": self.name,
            "balance": self.balance,
            "status": self.status.value,
            "plan": self.plan.value,
            "debt_limit": self.debt_limit
        }

class SubscriberPayload(BaseModel):
    phone_number: str
    name: str
    balance: float
    status: SubscriberStatus
    plan: BillingPlan
    debt_limit: float = 0.0
        