import json
import os
import redis

class BillingDB:
    def __init__(self, json_path):
        self.json_path = json_path
        # Connett to Redis; decode_responses=True to get strings instead of bytes
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    def load_to_redis(self):
        if not os.path.exists(self.json_path):
            print(f"File {self.json_path} does not exist.")
            return 0
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            subs = json.load(f)
            for s in subs:
                phone = s['phone_number']
                # Store balance as a separate key for easy access and updates
                self.redis_client.set(f"balance:{phone}", s['balance'])
                
                # Store other subscriber details in a hash
                self.redis_client.hset(f"user:{phone}", mapping={
                    "name": s['name'],
                    "status": s['status'],
                    "plan": s['plan'],
                    "debt_limit": s['debt_limit']
                    })
        return len(subs)

    def get_all_subscribers(self):
        subscribe_keys = self.redis_client.keys("user:*")
        all_subs = []
        for key in subscribe_keys:
            phone = key.split(":")[1]
            user_info = self.redis_client.hgetall(key)
            balance = self.redis_client.get(f"balance:{phone}")
            user_info['phone_number'] = phone
            user_info['balance'] = float(balance) if balance is not None else 0.0
            all_subs.append(user_info)
        return all_subs

    def save_subscriber(self, phone: str, data: dict, balance: float):
        # Update subscriber details in Redis
        self.redis_client.hset(f"user:{phone}", mapping=data)
        self.redis_client.set(f"balance:{phone}", balance)
        
    def delete_subscriber(self, phone: str):
        # Delete subscriber from Redis
        self.redis_client.delete(f"user:{phone}")
        self.redis_client.delete(f"balance:{phone}")

    def save_to_json(self):
        all_subs = self.get_all_subscribers()
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(all_subs, f, indent=4)
        print(f"Saved {len(all_subs)} subscribers to {self.json_path}.")
    
    def get_user(self, phone:str):
        # Get user details from Redis hash; balance is stored separately, so we need to get it as well
        return self.redis_client.hgetall(f"user:{phone}")
    
    def get_balance(self, phone:str):
        # Get balance from Redis
        return self.redis_client.get(f"balance:{phone}")
        
    def deduct_balance(self, phone:str, amount:float):
        # Deduct balance from Redis
        return self.redis_client.incrbyfloat(f"balance:{phone}", -amount)