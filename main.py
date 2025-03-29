import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.rest.models import api_router
from app.core.config import settings
from app.core.db import connect_to_mongodb, close_mongodb_connection
from app.api.grpc_server import serve as serve_grpc

# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB and start gRPC server
    await connect_to_mongodb()
    grpc_thread = threading.Thread(target=start_grpc_server, daemon=True)
    grpc_thread.start()
    yield  # Application runs here
    # Shutdown: Clean up MongoDB connection
    await close_mongodb_connection()

# Initialize FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    description="P4rth Sinha Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

def start_grpc_server():
    """Start the gRPC server."""
    grpc_server = serve_grpc()
    grpc_server.wait_for_termination()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)