from fastapi import APIRouter, HTTPException, status, Query, Path, Depends
from typing import List

from app.models.models import User, UserCreate, UserUpdate
from app.services.user_service import UserServices
from app.api.rest.auth import get_current_user

router = APIRouter()
user_service = UserServices()

@router.get("/users/", response_model=List[User])
async def read_users(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve users with pagination.
    Only available to admin users.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    return await user_service.get_users(skip=skip, limit=limit)

@router.get("/users/{user_id}", response_model=User)
async def read_user(
    user_id: str = Path(..., title="The ID of the user to get"),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user by ID.
    Users can get their own info, admins can get any user.
    """
    if current_user.role != "admin" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@router.get("/users/username/{username}", response_model=User)
async def read_user_by_username(username: str):
    """
    Get a specific user by username.
    Public endpoint.
    """
    user = await user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found"
        )
    return user

@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user.
    Public endpoint (registration).
    """
    try:
        return await user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str = Path(..., title="The ID of the user to update"),
    user: UserUpdate = None,
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing user.
    Users can update their own info, admins can update any user.
    Only admins can change roles.
    """
    # Only allow admins to change roles
    if current_user.role != "admin" and user.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to change role"
        )
        
    # Check permissions
    if current_user.role != "admin" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        updated_user = await user_service.update_user(user_id, user)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str = Path(..., title="The ID of the user to delete"),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a user.
    Users can delete their own account, admins can delete any user.
    """
    if current_user.role != "admin" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return None