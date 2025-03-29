import asyncio
import grpc
from concurrent import futures
from datetime import datetime, timedelta
from typing import Any

# Import generated protobuf code (to be generated)
# You'll need to run protoc to generate these files
import app.protos.service_pb2 as service_pb2
import app.protos.service_pb2_grpc as service_pb2_grpc

from app.core.config import settings
from app.models.models import User, UserCreate, UserUpdate
from app.models.models import Project, ProjectCreate, ProjectUpdate
from app.models.models import ProjectImage, ProjectImageCreate, ProjectImageUpdate
from app.services.user_service import UserServices
# from app.services.project_service import ProjectService
# from app.services.project_image_service import ProjectImageService
from app.api.rest.auth import create_access_token

# User Service Implementation
class UserServicer(service_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.service = UserServices()
    
    def _user_to_proto(self, user: Any) -> service_pb2.User:
        """Convert user model to protobuf message."""
        return service_pb2.User(
            id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role,
            created_at=user.created_at.isoformat()
        )
    
    async def GetUsers(self, request, context):
        """Get all users with pagination."""
        users = await self.service.get_users(skip=request.skip, limit=request.limit)
        
        response = service_pb2.GetUsersResponse()
        for user in users:
            user_proto = self._user_to_proto(user)
            response.users.append(user_proto)
        
        return response
    
    async def GetUser(self, request, context):
        """Get a user by their ID."""
        user = await self.service.get_user(request.id)
        
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User with ID {request.id} not found")
            return service_pb2.UserResponse()
        
        user_proto = self._user_to_proto(user)
        return service_pb2.UserResponse(user=user_proto)
    
    async def GetUserByUsername(self, request, context):
        """Get a user by their username."""
        user = await self.service.get_user_by_username(request.username)
        
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User with username {request.username} not found")
            return service_pb2.UserResponse()
        
        user_proto = self._user_to_proto(user)
        return service_pb2.UserResponse(user=user_proto)
    
    async def CreateUser(self, request, context):
        """Create a new user."""
        try:
            user_data = UserCreate(
                username=request.username,
                email=request.email,
                password=request.password,
                role=request.role
            )
            
            user = await self.service.create_user(user_data)
            user_proto = self._user_to_proto(user)
            
            return service_pb2.UserResponse(user=user_proto)
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return service_pb2.UserResponse()
    
    async def UpdateUser(self, request, context):
        """Update an existing user."""
        # Build update data from request
        update_data = {}
        
        # Only include fields that are explicitly set in the request
        for field, value in request.ListFields():
            if field.name != 'id':
                update_data[field.name] = value
        
        user_update = UserUpdate(**update_data)
        
        try:
            user = await self.service.update_user(request.id, user_update)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return service_pb2.UserResponse()
            
            user_proto = self._user_to_proto(user)
            return service_pb2.UserResponse(user=user_proto)
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return service_pb2.UserResponse()
    
    async def DeleteUser(self, request, context):
        """Delete a user by their ID."""
        success = await self.service.delete_user(request.id)
        
        if not success:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User with ID {request.id} not found")
        
        return service_pb2.DeleteUserResponse(success=success)
    
    async def AuthenticateUser(self, request, context):
        """Authenticate a user by username and password."""
        user = await self.service.authenticate_user(request.username, request.password)
        
        if not user:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid username or password")
            return service_pb2.AuthenticateUserResponse()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        user_proto = self._user_to_proto(user)
        return service_pb2.AuthenticateUserResponse(
            token=token,
            user=user_proto
        )

# Project Service Implementation
# class ProjectServicer(service_pb2_grpc.ProjectServiceServicer):
#     def __init__(self):
#         self.service = ProjectService()
    
#     def _project_image_to_proto(self, image: Any) -> service_pb2.ProjectImage:
#         """Convert a project image model to protobuf message."""
#         return service_pb2.ProjectImage(
#             id=str(image.id),
#             project_id=str(image.project_id),
#             image_url=image.image_url
#         )
    
#     def _project_to_proto(self, project: Any) -> service_pb2.Project:
#         """Convert a project model to protobuf message."""
#         project_proto = service_pb2.Project(
#             id=str(project.id),
#             slug=project.slug,
#             title=project.title,
#             body=project.body,
#             user_id=str(project.user_id),
#             created_at=project.created_at.isoformat(),
#             updated_at=project.updated_at.isoformat()
#         )
        
#         if project.github_link:
#             project_proto.github_link = project.github_link
        
#         # Add images
#         for image in project.images:
#             image_proto = self._project_image_to_proto(image)
#             project_proto.images.append(image_proto)
        
#         return project_proto
    
#     async def GetProjects(self, request, context):
#         """Get all projects with pagination."""
#         projects = await self.service.get_projects(skip=request.skip, limit=request.limit)
        
#         response = service_pb2.GetProjectsResponse()
#         for project in projects:
#             project_proto = self._project_to_proto(project)
#             response.projects.append(project_proto)
        
#         return response
    
#     async def GetProject(self, request, context):
#         """Get a project by its ID."""
#         project = await self.service.get_project(request.id)
        
#         if not project:
#             context.set_code(grpc.StatusCode.NOT_FOUND)
#             context.set_details(f"Project with ID {request.id} not found")
#             return service_pb2.ProjectResponse()
        
#         project_proto = self._project_to_proto(project)
#         return service_pb2.ProjectResponse(project=project_proto)
    
#     async def GetProjectBySlug(self, request, context):
#         """Get a project by its slug."""
#         project = await self.service.get_project_by_slug(request.slug)
        
#         if not project:
#             context.set_code(grpc.StatusCode.NOT_FOUND)
#             context.set_details(f"Project with slug {request.slug} not found")
#             return service_pb2.ProjectResponse()
        
#         project_proto = self._project_to_proto(project)
#         return service_pb2.ProjectResponse(project=project_proto)
    
#     async def GetProjectsByUser(self, request, context):
#         """Get all projects for a specific user."""
#         projects = await self.service.get_projects_by_user(
#             user_id=request.user_id,
#             skip=request.skip,
#             limit=request.limit
#         )
        
#         response = service_pb2.GetProjectsResponse()
#         for project in projects:
#             project_proto = self._project_to_proto(project)
#             response.projects.append(project_proto)
        
#         return response
    
#     async def CreateProject(self, request, context):
#         """Create a new project."""
#         try:
#             github_link = request.github_link if hasattr(request, 'github_link') else None
            
#             project_data = ProjectCreate(
#                 slug=request.slug,
#                 title=request.title,
#                 body=request.body,
#                 github_link=github_link,
#                 user_id=request.user_id
#             )
            
#             project = await self.service.create_project(project_data)
#             project_proto = self._project_to_proto(project)
            
#             return service_pb2.ProjectResponse(project=project_proto)
#         except ValueError as e:
#             context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
#             context.set_details(str(e))
#             return service_pb2.ProjectResponse()
    
#     async def UpdateProject(self, request, context):
#         """Update an existing project."""
#         # Build update data from request
#         update_data = {}
        
#         # Only include fields that are explicitly set in the request
#         for field, value in request.ListFields():
#             if field.name != 'id':
#                 update_data[field.name] = value
        
#         project_update = ProjectUpdate(**update_data)
        
#         try:
#             project = await self.service.update_project(request.id, project_update)
            
#             if not project:
#                 context.set_code(grpc.StatusCode.NOT_FOUND)
#                 context.set_details(f"Project with ID {request.id} not found")
#                 return service_pb2.ProjectResponse()
            
#             project_proto = self._project_to_proto(project)
#             return service_pb2.ProjectResponse(project=project_proto)
#         except ValueError as e:
#             context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
#             context.set_details(str(e))
#             return service_pb2.ProjectResponse()
    
#     async def DeleteProject(self, request, context):
#         """Delete a project by its ID."""
#         success = await self.service.delete_project(request.id)
        
#         if not success:
#             context.set_code(grpc.StatusCode.NOT_FOUND)
#             context.set_details(f"Project with ID {request.id} not found")
        
#         return service_pb2.DeleteProjectResponse(success=success)

# # Project Image Service Implementation
# class ProjectImageServicer(service_pb2_grpc.ProjectImageServiceServicer):
#     def __init__(self):
#         self.service = ProjectImageService()
    
#     def _project_image_to_proto(self, image: Any) -> service_pb2.ProjectImage:
#         """Convert a project image model to protobuf message."""
#         return service_pb2.ProjectImage(
#             id=str(image.id),
#             project_id=str(image.project_id),
#             image_url=image.image_url
#         )
    
#     async def GetImagesByProject(self, request, context):
#         """Get all images for a specific project."""
#         images = await self.service.get_images_by_project(request.project_id)
        
#         response = service_pb2.GetProjectImagesResponse()
#         for image in images:
#             image_proto = self._project_image_to_proto(image)
#             response.images.append(image_proto)
        
#         return response
    
#     async def GetImage(self, request, context):
#         """Get an image by its ID."""
#         image = await self.service.get_image(request.id)
        
#         if not image:
#             context.set_code(grpc.StatusCode.NOT_FOUND)
#             context.set_details(f"Image with ID {request.id} not found")
#             return service_pb2.ProjectImageResponse()
        
#         image_proto = self._project_image_to_proto(image)
#         return service_pb2.ProjectImageResponse(image=image_proto)
    
#     async def CreateImage(self, request, context):
#         """Create a new image."""
#         try:
#             image_data = ProjectImageCreate(
#                 project_id=request.project_id,
#                 image_url=request.image_url
#             )
            
#             image = await self.service.create_image(image_data)
#             image_proto = self._project_image_to_proto(image)
            
#             return service_pb2.ProjectImageResponse(image=image_proto)
#         except ValueError as e:
#             context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
#             context.set_details(str(e))
#             return service_pb2.ProjectImageResponse()
    
#     async def UpdateImage(self, request, context):
#         """Update an existing image."""
#         # Build update data from request
#         update_data = {}
        
#         # Only include fields that are explicitly set in the request
#         for field, value in request.ListFields():
#             if field.name != 'id':
#                 update_data[field.name] = value
        
#         image_update = ProjectImageUpdate(**update_data)
        
#         try:
#             image = await self.service.update_image(request.id, image_update)
            
#             if not image:
#                 context.set_code(grpc.StatusCode.NOT_FOUND)
#                 context.set_details(f"Image with ID {request.id} not found")
#                 return service_pb2.ProjectImageResponse()
            
#             image_proto = self._project_image_to_proto(image)
#             return service_pb2.ProjectImageResponse(image=image_proto)
#         except ValueError as e:
#             context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
#             context.set_details(str(e))
#             return service_pb2.ProjectImageResponse()
    
#     async def DeleteImage(self, request, context):
#         """Delete an image by its ID."""
#         success = await self.service.delete_image(request.id)
        
#         if not success:
#             context.set_code(grpc.StatusCode.NOT_FOUND)
#             context.set_details(f"Image with ID {request.id} not found")
        
#         return service_pb2.DeleteImageResponse(success=success)

# Adapter classes for async-to-sync conversion
class AsyncUserServicer(service_pb2_grpc.UserServiceServicer):
    """Adapter for running async methods in gRPC."""
    def __init__(self):
        self.servicer = UserServicer()
    
    def GetUsers(self, request, context):
        return asyncio.run(self.servicer.GetUsers(request, context))
    
    def GetUser(self, request, context):
        return asyncio.run(self.servicer.GetUser(request, context))
    
    def GetUserByUsername(self, request, context):
        return asyncio.run(self.servicer.GetUserByUsername(request, context))
    
    def CreateUser(self, request, context):
        return asyncio.run(self.servicer.CreateUser(request, context))
    
    def UpdateUser(self, request, context):
        return asyncio.run(self.servicer.UpdateUser(request, context))
    
    def DeleteUser(self, request, context):
        return asyncio.run(self.servicer.DeleteUser(request, context))
    
    def AuthenticateUser(self, request, context):
        return asyncio.run(self.servicer.AuthenticateUser(request, context))

# class AsyncProjectServicer(service_pb2_grpc.ProjectServiceServicer):
#     """Adapter for running async methods in gRPC."""
#     def __init__(self):
#         self.servicer = ProjectServicer()
    
#     def GetProjects(self, request, context):
#         return asyncio.run(self.servicer.GetProjects(request, context))
    
#     def GetProject(self, request, context):
#         return asyncio.run(self.servicer.GetProject(request, context))
    
#     def GetProjectBySlug(self, request, context):
#         return asyncio.run(self.servicer.GetProjectBySlug(request, context))
    
#     def GetProjectsByUser(self, request, context):
#         return asyncio.run(self.servicer.GetProjectsByUser(request, context))
    
#     def CreateProject(self, request, context):
#         return asyncio.run(self.servicer.CreateProject(request, context))
    
#     def UpdateProject(self, request, context):
#         return asyncio.run(self.servicer.UpdateProject(request, context))
    
#     def DeleteProject(self, request, context):
#         return asyncio.run(self.servicer.DeleteProject(request, context))

# class AsyncProjectImageServicer(service_pb2_grpc.ProjectImageServiceServicer):
#     """Adapter for running async methods in gRPC."""
#     def __init__(self):
#         self.servicer = ProjectImageServicer()
    
#     def GetImagesByProject(self, request, context):
#         return asyncio.run(self.servicer.GetImagesByProject(request, context))
    
#     def GetImage(self, request, context):
#         return asyncio.run(self.servicer.GetImage(request, context))
    
#     def CreateImage(self, request, context):
#         return asyncio.run(self.servicer.CreateImage(request, context))
    
#     def UpdateImage(self, request, context):
#         return asyncio.run(self.servicer.UpdateImage(request, context))
    
#     def DeleteImage(self, request, context):
#         return asyncio.run(self.servicer.DeleteImage(request, context))

def serve():
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add servicers to server
    service_pb2_grpc.add_UserServiceServicer_to_server(
        AsyncUserServicer(), server
    )
    # service_pb2_grpc.add_ProjectServiceServicer_to_server(
    #     AsyncProjectServicer(), server
    # )
    # service_pb2_grpc.add_ProjectImageServiceServicer_to_server(
    #     AsyncProjectImageServicer(), server
    # )
    
    server.add_insecure_port(settings.GRPC_SERVER_ADDRESS)
    server.start()
    print(f"gRPC server started on {settings.GRPC_SERVER_ADDRESS}")
    return server