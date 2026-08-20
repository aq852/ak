from datetime import datetime, timedelta
import random
import string
from utils.database import db

class TokenManager:
    """VIP Token management"""
    
    @staticmethod
    async def generate_token(admin_id: int, days: int = 30, token_type: str = "vip") -> str:
        """Generate a VIP token"""
        # Generate random token code
        token_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        token = f"{token_type.upper()}-{token_code[:4]}-{token_code[4:8]}-{token_code[8:]}"
        
        await db.tokens.insert_one({
            "token": token,
            "type": token_type,
            "days": days,
            "created_by": admin_id,
            "created_at": datetime.utcnow(),
            "used": False,
            "used_by": None,
            "used_at": None
        })
        
        return token
    
    @staticmethod
    async def redeem_token(user_id: int, token: str) -> tuple:
        """Redeem a token"""
        token_doc = await db.tokens.find_one({"token": token})
        
        if not token_doc:
            return False, "Invalid token"
        
        if token_doc.get("used"):
            return False, "Token already used"
        
        # Mark as used
        await db.tokens.update_one(
            {"token": token},
            {"$set": {"used": True, "used_by": user_id, "used_at": datetime.utcnow()}}
        )
        
        # Add VIP to user (imported from UserManager to avoid circular import)
        from utils.user_manager import UserManager
        await UserManager.add_vip(user_id, token_doc["days"])
        
        return True, f"Successfully activated {token_doc['days']} days of VIP!"
    
    @staticmethod
    async def get_token_stats():
        """Get token usage statistics"""
        pipeline = [
            {"$group": {
                "_id": "$type",
                "total": {"$sum": 1},
                "used": {"$sum": {"$cond": ["$used", 1, 0]}},
                "unused": {"$sum": {"$cond": ["$used", 0, 1]}}
            }}
        ]
        
        results = await db.tokens.aggregate(pipeline).to_list(length=None)
        return results

class AdManager:
    """Sponsored Ads management"""
    
    @staticmethod
    async def create_ad(text: str, button_url: str, button_text: str = "Learn More", 
                       is_active: bool = True):
        """Create a new sponsored ad"""
        await db.ads.insert_one({
            "text": text,
            "button_url": button_url,
            "button_text": button_text,
            "is_active": is_active,
            "views": 0,
            "clicks": 0,
            "created_at": datetime.utcnow()
        })
    
    @staticmethod
    async def get_random_ad() -> dict:
        """Get a random active ad"""
        ads = await db.ads.find({"is_active": True}).to_list(length=None)
        if not ads:
            return None
        return random.choice(ads)
    
    @staticmethod
    async def increment_views(ad_id):
        """Increment ad view count"""
        from bson import ObjectId
        await db.ads.update_one(
            {"_id": ObjectId(ad_id)},
            {"$inc": {"views": 1}}
        )
    
    @staticmethod
    async def increment_clicks(ad_id):
        """Increment ad click count"""
        from bson import ObjectId
        await db.ads.update_one(
            {"_id": ObjectId(ad_id)},
            {"$inc": {"clicks": 1}}
        )
    
    @staticmethod
    async def get_all_ads():
        """Get all ads"""
        return await db.ads.find().to_list(length=None)
    
    @staticmethod
    async def toggle_ad(ad_id, is_active: bool):
        """Toggle ad active status"""
        from bson import ObjectId
        await db.ads.update_one(
            {"_id": ObjectId(ad_id)},
            {"$set": {"is_active": is_active}}
        )
    
    @staticmethod
    async def delete_ad(ad_id):
        """Delete an ad"""
        from bson import ObjectId
        await db.ads.delete_one({"_id": ObjectId(ad_id)})

class RateLimiter:
    """Rate limiting for anti-spam"""
    
    # In-memory storage for rate limiting (for production, use Redis)
    _user_requests = {}
    
    @staticmethod
    def is_rate_limited(user_id: int, limit: int = 10, window: int = 60) -> bool:
        """Check if user is rate limited
        
        Args:
            user_id: User ID
            limit: Max requests per window
            window: Time window in seconds
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window)
        
        if user_id not in RateLimiter._user_requests:
            RateLimiter._user_requests[user_id] = []
        
        # Clean old requests
        RateLimiter._user_requests[user_id] = [
            req_time for req_time in RateLimiter._user_requests[user_id]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(RateLimiter._user_requests[user_id]) >= limit:
            return True
        
        # Add current request
        RateLimiter._user_requests[user_id].append(now)
        return False
    
    @staticmethod
    def get_remaining_requests(user_id: int, limit: int = 10, window: int = 60) -> int:
        """Get remaining requests for user"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window)
        
        if user_id not in RateLimiter._user_requests:
            return limit
        
        # Clean old requests
        RateLimiter._user_requests[user_id] = [
            req_time for req_time in RateLimiter._user_requests[user_id]
            if req_time > window_start
        ]
        
        return max(0, limit - len(RateLimiter._user_requests[user_id]))
