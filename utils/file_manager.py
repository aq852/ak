from datetime import datetime
import hashlib
from utils.database import db

class FileManager:
    """File management operations"""
    
    @staticmethod
    async def save_file(file_id: str, file_name: str, file_size: int, 
                       file_type: str, user_id: int, caption: str = None, tags: list = None):
        """Save a new file to database with duplicate detection"""
        
        # Create hash for duplicate detection
        file_hash = hashlib.md5(f"{file_name}{file_size}".encode()).hexdigest()
        
        # Check for duplicates
        existing = await db.files.find_one({
            "$or": [
                {"file_name": file_name, "file_size": file_size},
                {"file_hash": file_hash}
            ]
        })
        
        if existing:
            return False, existing  # Duplicate found
        
        # Save new file
        await db.files.insert_one({
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type,  # video, document, audio, photo
            "user_id": user_id,
            "caption": caption,
            "tags": tags or [],
            "file_hash": file_hash,
            "downloads": 0,
            "created_at": datetime.utcnow(),
            "last_downloaded": None
        })
        
        return True, None
    
    @staticmethod
    async def get_file(file_id: str):
        """Get file by file_id"""
        return await db.files.find_one({"file_id": file_id})
    
    @staticmethod
    async def search_files(query: str, filters: dict = None, limit: int = 20):
        """Search files with fuzzy matching and filters"""
        search_query = {}
        
        # Text search
        if query:
            search_query["$text"] = {"$search": query}
        
        # Apply filters
        if filters:
            if filters.get("file_type"):
                search_query["file_type"] = filters["file_type"]
            if filters.get("min_size"):
                search_query["file_size"] = {"$gte": filters["min_size"]}
            if filters.get("max_size"):
                search_query.setdefault("file_size", {})["$lte"] = filters["max_size"]
        
        # Execute search with score
        results = db.files.find(search_query).sort([("downloads", -1)]).limit(limit)
        return await results.to_list(length=limit)
    
    @staticmethod
    async def increment_downloads(file_id: str):
        """Increment file download count"""
        await db.files.update_one(
            {"file_id": file_id},
            {
                "$inc": {"downloads": 1},
                "$set": {"last_downloaded": datetime.utcnow()}
            }
        )
    
    @staticmethod
    async def get_trending_files(days: int = 7, limit: int = 10):
        """Get trending files based on downloads in last N days"""
        since = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"last_downloaded": {"$gte": since}}},
            {"$sort": {"downloads": -1}},
            {"$limit": limit}
        ]
        
        results = db.files.aggregate(pipeline)
        return await results.to_list(length=limit)
    
    @staticmethod
    async def delete_file(file_id: str):
        """Delete a file from database"""
        await db.files.delete_one({"file_id": file_id})
    
    @staticmethod
    async def get_file_count() -> int:
        """Get total file count"""
        return await db.files.count_documents({})
    
    @staticmethod
    async def get_all_files():
        """Get all files"""
        return db.files.find({})
    
    @staticmethod
    async def update_file_caption(file_id: str, new_caption: str):
        """Update file caption"""
        await db.files.update_one(
            {"file_id": file_id},
            {"$set": {"caption": new_caption}}
        )
    
    @staticmethod
    async def add_tags(file_id: str, tags: list):
        """Add tags to a file"""
        await db.files.update_one(
            {"file_id": file_id},
            {"$addToSet": {"tags": {"$each": tags}}}
        )
