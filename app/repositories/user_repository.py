from bson import ObjectId
from typing import List, Optional
from datetime import datetime
import hashlib
import os

from app.core.db import db
from app.models.models import User, UserCreate, UserUpdate, UserInDB

class UserRepository:
    collection_name = "users"
    
    def _hash_password(self, password: str) -> str:
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + ':' + key.hex()
    
    def _verify_password(self, stored_password: str, provided_password: str) -> bool:
        salt_hex, key_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        stored_key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return new_key == stored_key
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        users = []
        cursor = db.db[self.collection_name].find().skip(skip).limit(limit)
        async for document in cursor:
            user_dict = { k: v for k, v in document.items() if k != 'password_hash' }
            users.append(User(**user_dict))
        return users
    
    async def get_by_id(self, id: str) -> Optional[User]:
        if not ObjectId.is_valid(id):
            return None
        
        document = await db.db[self.collection_name].find_one({"_id": ObjectId(id)})
        if document:
            user_dict = { k: v for k, v in document.items() if k != 'password_hash' }
            return User(**user_dict)
        return None
    
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        document = await db.db[self.collection_name].find_one({ "email": email })
        if document:
            return UserInDB(**document)
        return None
    
    async def get_by_username(self, username: str) -> Optional[UserInDB]:
        document = await db.db[self.collection_name].find_one({"username": username})
        if document:
            return UserInDB(**document)
        return None
    
    async def create(self, user: UserCreate) -> User:
        existing_username = await self.get_by_username(user.username)
        if existing_username:
            raise ValueError("Username alredy exists")
        
        existing_email = await self.get_by_email(user.email)
        if existing_email:
            raise ValueError("Email already exists")
        
        # Create user with hashed password
        user_dict = user.dict()
        password = user_dict.pop("password")
        password_hash = self._hash_password(password)
        
        user_data = {
            **user_dict,
            "password_hash": password_hash,
            "created_at": datetime.utcnow()
        }
        
        result = await db.db[self.collection_name].insert_one(user_data)
        
        if result.inserted_id:
            return await self.get_by_id(str(result.inserted_id))
        return None
    
    async def update(self, id: str, user: UserUpdate) -> Optional[User]:
        if not ObjectId.is_valid(id):
            return None
        
        # Filter not None values
        update_data = { k: v for k, v in user.model_dump().items if v is not None }
        
        if update_data:
            if "password" in update_data:
                password = update_data.pop("password")
                update_data["password_hash"] = self._hash_password(password)
                
            if "username" in update_data:
                existing = await self.get_by_username(update_data["username"])
                if existing and str(existing.id) != id:
                    raise ValueError("Username already exists")
                
            if "email" in update_data:
                existing = await self.get_by_email(update_data["email"])
                if existing and str(existing.id) != id:
                    raise ValueError("Email already exists")
                
            await db.db[self.collection_name].update_one(
                {"_id": ObjectId(id)},
                {"$set": update_data}
            )
            
        return await self.get_by_id(id)
    
    async def delete(self, id: str) -> bool:
        if not ObjectId.is_valid(id):
            return False
        
        result = await db.db[self.collection_name].delete_one({"_id": ObjectId(id)})
        return result.delete_count > 0
    
    async def authenticate(self, username: str, password: str) -> Optional[User]:
        user = await self.get_by_username(username)
        if not user:
            return None
        
        if not self._verify_password(user.password_hash, password):
            return None
        
        # Return user without password_hash
        user_dict = { k: v for k, v in user.model_dump().items() if k != 'password_hash' }
        return User(**user_dict)