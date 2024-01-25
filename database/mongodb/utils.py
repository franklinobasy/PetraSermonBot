from datetime import datetime, timedelta

from jose import JWTError, jwt

from database.mongodb import users_collection, access_tokens_collection
from .models import User, UserCreate, AccessToken, TokenCreate


def get_user_by_email(email: str) -> User:
    user_data = users_collection.find_one({"email": email})
    if user_data:
        return User(**user_data)
    return None

def create_user(user_create: UserCreate) -> User:
    user_data = user_create.dict()
    result = users_collection.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    return User(**user_data)

def update_user(user_id: str, user_update: UserCreate) -> User:
    updated_user = users_collection.find_one_and_update(
        {"_id": user_id},
        {"$set": user_update.dict(exclude_unset=True)},
        return_document=True
    )
    if updated_user:
        return User(**updated_user)
    return None

def delete_user(user_id: str) -> bool:
    result = users_collection.delete_one({"_id": user_id})
    return result.deleted_count > 0

def get_access_token(user_id: str) -> AccessToken:
    token_data = access_tokens_collection.find_one({"user_id": user_id, "expires_at": {"$gt": datetime.utcnow()}})
    if token_data:
        return AccessToken(**token_data)
    return None

def create_access_token(token_create: TokenCreate) -> AccessToken:
    access_token_expires = timedelta(minutes=24 * 60)  # 24 hours
    expires = datetime.utcnow() + access_token_expires
    to_encode = {"sub": token_create.user_id, "exp": expires}
    access_token = jwt.encode(to_encode, token_create.secret_key, algorithm=token_create.algorithm)

    result = access_tokens_collection.update_one(
        {"user_id": token_create.user_id},
        {"$set": {"access_token": access_token, "expires_at": expires}},
        upsert=True,
    )

    return AccessToken(access_token=access_token, token_type="bearer")

def delete_access_token(user_id: str) -> bool:
    result = access_tokens_collection.delete_one({"user_id": user_id})
    return result.deleted_count > 0