from datetime import datetime, timedelta
from utils.database import db

class UserManager:
    """User management operations"""
    
    @staticmethod
    async def get_user(user_id: int):
        """Get user by ID"""
        return await db.users.find_one({"user_id": user_id})
    
    @staticmethod
    async def create_user(user_id: int, username: str = None, language: str = "en"):
        """Create a new user"""
        user = await UserManager.get_user(user_id)
        if not user:
            referral_code = f"REF{user_id}{datetime.now().strftime('%Y%m%d')}"
            await db.users.insert_one({
                "user_id": user_id,
                "username": username,
                "language": language,
                "is_vip": False,
                "vip_expiry": None,
                "referral_code": referral_code,
                "referred_by": None,
                "downloads_today": 0,
                "total_downloads": 0,
                "points": 0,
                "is_banned": False,
                "created_at": datetime.utcnow(),
                "last_active": datetime.utcnow()
            })
            return await UserManager.get_user(user_id)
        return user
    
    @staticmethod
    async def update_last_active(user_id: int):
        """Update user's last active timestamp"""
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"last_active": datetime.utcnow()}}
        )
    
    @staticmethod
    async def is_vip(user_id: int) -> bool:
        """Check if user is VIP"""
        user = await UserManager.get_user(user_id)
        if not user or not user.get("is_vip"):
            return False
        
        # Check if VIP has expired
        vip_expiry = user.get("vip_expiry")
        if vip_expiry and datetime.utcnow() > vip_expiry:
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_vip": False}}
            )
            return False
        return True
    
    @staticmethod
    async def is_banned(user_id: int) -> bool:
        """Check if user is banned"""
        user = await UserManager.get_user(user_id)
        return user.get("is_banned", False) if user else False
    
    @staticmethod
    async def ban_user(user_id: int):
        """Ban a user"""
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": True}}
        )
    
    @staticmethod
    async def unban_user(user_id: int):
        """Unban a user"""
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": False}}
        )
    
    @staticmethod
    async def add_vip(user_id: int, days: int):
        """Add VIP access to user"""
        user = await UserManager.get_user(user_id)
        if user and user.get("vip_expiry"):
            new_expiry = user["vip_expiry"] + timedelta(days=days)
        else:
            new_expiry = datetime.utcnow() + timedelta(days=days)
        
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_vip": True, "vip_expiry": new_expiry}}
        )
    
    @staticmethod
    async def increment_downloads(user_id: int):
        """Increment user's download count"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$inc": {"downloads_today": 1, "total_downloads": 1},
                "$set": {"last_download_reset": today}
            }
        )
    
    @staticmethod
    async def get_download_count(user_id: int) -> int:
        """Get user's download count for today"""
        user = await UserManager.get_user(user_id)
        if not user:
            return 0
        
        # Reset if new day
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        last_reset = user.get("last_download_reset")
        if not last_reset or last_reset < today:
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"downloads_today": 0, "last_download_reset": today}}
            )
            return 0
        
        return user.get("downloads_today", 0)
    
    @staticmethod
    async def add_referral(user_id: int, referrer_code: str):
        """Add referral relationship"""
        referrer = await db.users.find_one({"referral_code": referrer_code})
        if referrer and referrer["user_id"] != user_id:
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"referred_by": referrer["user_id"]}}
            )
            # Bonus for both users (1 day VIP)
            await UserManager.add_vip(user_id, 1)
            await UserManager.add_vip(referrer["user_id"], 1)
            return True
        return False
    
    @staticmethod
    async def get_all_users():
        """Get all users"""
        return db.users.find({})
    
    @staticmethod
    async def get_user_count() -> int:
        """Get total user count"""
        return await db.users.count_documents({})
    
    @staticmethod
    async def get_new_users_today() -> int:
        """Get new users count for today"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return await db.users.count_documents({"created_at": {"$gte": today}})
