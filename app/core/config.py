import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = "P4rth Project Backend"
    API_PREFIX: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # MongoDB Settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "project_db")
    
    # gRPC Settings
    GRPC_SERVER_ADDRESS: str = os.getenv("GRPC_SERVER_ADDRESS", "[::]:50051")
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "testpassword")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
settings = Settings()