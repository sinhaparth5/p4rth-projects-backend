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
    
    