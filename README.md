# P4rth Projects Backend

This project provides a complete backend solution with:
- FastAPI for REST API
- MongoDB for database
- gRPC for high-performance API communication

## Features

- Complete CRUD operations on items collection
- Both REST API and gRPC interfaces
- Clean architecture with separation of concerns
- Docker support

## Project Structure

```
app/
│
├── api/
│   ├── __init__.py
│   ├── grpc_server.py
│   └── rest/
│       ├── __init__.py
│       ├── endpoints.py
│       └── models.py
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── db.py
│
├── models/
│   ├── __init__.py
│   └── item.py
│
├── protos/
│   └── service.proto
│
├── repositories/
│   ├── __init__.py
│   └── item_repository.py
│
├── services/
│   ├── __init__.py
│   └── item_service.py
│
├── main.py
├── requirements.txt
└── Dockerfile
```

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB instance
- Docker (optional)

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
DEBUG=False
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=fastapi_db
GRPC_SERVER_ADDRESS=[::]:50051
```

### Local Development

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Generate gRPC Python code:
```bash
python -m grpc_tools.protoc -I./app/protos --python_out=./app/protos --grpc_python_out=./app/protos ./app/protos/service.proto
```

4. Run the application:
```bash
python app/main.py
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t fastapi-mongodb-grpc .
```

2. Run the container:
```bash
docker run -p 8000:8000 -p 50051:50051 --env-file .env fastapi-mongodb-grpc
```

## API Documentation

Once the application is running, you can access the Swagger documentation at:
```
http://localhost:8000/docs
```

## Using gRPC

The gRPC server runs on port 50051. You can use tools like [grpcurl](https://github.com/fullstorydev/grpcurl) or [BloomRPC](https://github.com/uw-labs/bloomrpc) to interact with the gRPC API.

Example gRPC client (Python):

```python
import grpc
import service_pb2
import service_pb2_grpc

# Create a gRPC channel
with grpc.insecure_channel('localhost:50051') as channel:
    # Create a stub (client)
    stub = service_pb2_grpc.ItemServiceStub(channel)
    
    # Make gRPC calls
    response = stub.GetItems(service_pb2.GetItemsRequest(skip=0, limit=10))
    print(f"Found {len(response.items)} items")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
