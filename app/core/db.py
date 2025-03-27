from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None
    
db = Database()

async def connect_to_mongodb():
    """ Connect to MongoDB """
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.MONGODB_DB_NAME]
    
    # Create indexes for optimized lookups
    await create_indexes()
    
    print(f"Connected to MongoDB at {settings.MONGODB_URL}")
    
async def close_mongodb_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")
        
async def create_indexes():
    """ Create neccessary indexes for MongoDB collections """
    # User indexes
    await db.db.users.create_indexes("username", unique=True)
    await db.db.users.create_indexes("email", unique=True)
    
    # Project indexes
    await db.db.projects.create_indexes("slug", unique=True)
    await db.db.projects.create_indexes("user_id")
    
    # Project image indexes
    await db.db.project_images.create_indexes("project_id")