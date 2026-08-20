from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import Config

class Database:
    """MongoDB Database Handler"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.users = None
        self.files = None
        self.groups = None
        self.settings = None
        self.ads = None
        self.payments = None
        self.tokens = None
    
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        
        # Collections
        self.users = self.db["users"]
        self.files = self.db["files"]
        self.groups = self.db["groups"]
        self.settings = self.db["settings"]
        self.ads = self.db["ads"]
        self.payments = self.db["payments"]
        self.tokens = self.db["tokens"]
        
        # Create indexes for better performance
        await self.files.create_index([("file_name", "text"), ("tags", "text")])
        await self.files.create_index("file_id", unique=True)
        await self.users.create_index("user_id", unique=True)
        await self.users.create_index("referral_code", unique=True, sparse=True)
        await self.ads.create_index("is_active")
        
        print("✅ Connected to MongoDB")
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("❌ Disconnected from MongoDB")

# Global database instance
db = Database()
