from typing import List, Optional

from app.models.models import User, UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository

class UserServices:
    def __init__(self):
        self.repository = UserRepository()
        
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return await self.repository.get_all(skip, limit)
    
    async def get_user(self, id: str) -> Optional[User]:
        return await self.repository.get_by_id(id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        user = await self.repository.get_by_username(username)
        
        if user:
            user_dict = { k: v for k, v in user.dict().items() if k != 'password_hash' }
            return User(**user_dict)
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        user = await self.repository.get_by_email(email)
        if user:
            # Convert to User model (without password_hash)
            user_dict = {k: v for k, v in user.dict().items() if k != 'password_hash'}
            return User(**user_dict)
        return None
    
    async def create_user(self, user: UserCreate) -> User:
        return await self.repository.create(user)
    
    async def update_user(self, id: str, user: UserUpdate) -> Optional[User]:
        return await self.repository.update(id, user)
    
    async def delete_user(self, id: str) -> bool:
        return await self.repository.delete(id)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        return await self.repository.authenticate(username, password)