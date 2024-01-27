"""
Module Name: database.mongodb.utils

Description:
This module provides functions for user management and token authentication using MongoDB. It includes utilities for creating, retrieving, updating, and deleting user information in the database, as well as generating and managing access tokens for user authentication.

Dependencies:
- jose: JSON Web Token (JWT) library
- pymongo: MongoDB driver for Python
- models: User, AccessToken, TokenCreate models defined in the 'models' module
- database.mongodb: MongoDB collections for users and access tokens
- JWT_SECRET, JWT_ALGORITHM: Constants representing the secret key and algorithm for JWT encoding and decoding

Functions:
- create_user(user_create: User) -> User:
    Creates a new user in the database. If a user with the same email already exists, returns the existing user.

- get_user_by_email(email: str) -> User:
    Retrieves a user from the database based on their email.

- update_user(user_id: str, user_update: dict) -> User:
    Updates a user's information in the database.

- delete_user(user_id: str) -> bool:
    Deletes a user from the database.

- create_access_token(token_create: TokenCreate) -> AccessToken:
    Creates a new access token for a user. If an existing non-expired token is found, returns the existing token.

- get_access_token(user_id: str) -> Optional[AccessToken]:
    Retrieves an access token for a user. Returns None if no valid token is found.

- delete_access_token(user_id: str) -> bool:
    Deletes an access token for a user. Returns True if a token was successfully deleted.

- validate_access_token(access_token: str) -> Optional[AccessToken]:
    Validates an access token. Returns the validated access token if associated with a valid user_id and not expired. Returns None if the token is invalid.

Note:
Ensure that JWT_SECRET and JWT_ALGORITHM are properly configured with the secret key and algorithm for JWT encoding and decoding.
"""


from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from database.mongodb import users_collection, access_tokens_collection, JWT_SECRET, JWT_ALGORITHM
from ..models import User, AccessToken, TokenCreate


def create_user(user_create: User) -> User:
    """
    Creates a new user in the database.

    Parameters:
    - user_create (User): User object containing user information.

    Returns:
    User: The created user or the existing user if the email is not unique.
    """
    existing_user = users_collection.find_one({"email": user_create.email})
    
    if existing_user:
        return User(**existing_user)

    user_data = user_create.dict()
    result = users_collection.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    
    return User(**user_data)


def get_user_by_email(email: str) -> User:
    """
    Retrieves a user from the database based on their email.

    Parameters:
    - email (str): Email address of the user.

    Returns:
    User: The user with the specified email, or None if not found.
    """
    user_data = users_collection.find_one({"email": email})
    if user_data:
        return User(**user_data)
    return None


def update_user(user_id: str, user_update: dict) -> User:
    """
    Updates a user's information in the database.

    Parameters:
    - user_id (str): ID of the user to be updated.
    - user_update (dict): Dictionary containing updated user information.

    Returns:
    User: The updated user or None if the user with the specified ID is not found.
    """
    updated_user = users_collection.find_one_and_update(
        {"user_id": user_id},
        {"$set": user_update},
        return_document=True
    )
    if updated_user:
        return User(**updated_user)
    return None


def delete_user(user_id: str) -> bool:
    """
    Deletes a user from the database.

    Parameters:
    - user_id (str): ID of the user to be deleted.

    Returns:
    bool: True if the user was successfully deleted, False otherwise.
    """
    result = users_collection.delete_one({"user_id": user_id})
    return result.deleted_count > 0


def create_access_token(token_create: TokenCreate) -> AccessToken:
    """
    Creates a new access token for a user.

    Parameters:
    - token_create (TokenCreate): TokenCreate object containing token creation information.

    Returns:
    AccessToken: The created access token or the existing token if not expired.
    """
    existing_token = access_tokens_collection.find_one({
        "user_id": token_create.user_id,
        "expires_at": {"$gt": datetime.utcnow()}
    })

    if existing_token:
        return AccessToken(**existing_token)

    expires = token_create.expires_at
    to_encode = {"sub": token_create.user_id, "exp": expires}
    access_token = jwt.encode(to_encode, token_create.secret_key, algorithm=token_create.algorithm)

    result = access_tokens_collection.update_one(
        {"user_id": token_create.user_id},
        {"$set": {"access_token": access_token, "expires_at": expires}},
        upsert=True,
    )

    return AccessToken(user_id=token_create.user_id, access_token=access_token, token_type="bearer", expires_at=expires)


def get_access_token(user_id: str) -> Optional[AccessToken]:
    """
    Retrieves an access token for a user.

    Parameters:
    - user_id (str): ID of the user.

    Returns:
    Optional[AccessToken]: The access token if found and not expired, or None otherwise.
    """
    token_data = access_tokens_collection.find_one({"user_id": user_id, "expires_at": {"$gt": datetime.utcnow()}})
    return AccessToken(**token_data) if token_data else None


def delete_access_token(user_id: str) -> bool:
    """
    Deletes an access token for a user.

    Parameters:
    - user_id (str): ID of the user.

    Returns:
    bool: True if the access token was successfully deleted, False otherwise.
    """
    result = access_tokens_collection.delete_one({"user_id": user_id})
    print(f"Deletion result for user {user_id}: {result}")
    return result.deleted_count > 0


def validate_access_token(access_token: str) -> Optional[AccessToken]:
    """
    Validates an access token.

    Parameters:
    - access_token (str): The access token to be validated.

    Returns:
    Optional[AccessToken]: The validated access token if it is associated with a valid user_id and not expired.
                          Returns None if the token is invalid.
    """
    try:
        decoded_token = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = decoded_token.get("sub")

        # Check if the user_id exists and the token is not expired
        token_data = access_tokens_collection.find_one({"user_id": user_id, "expires_at": {"$gt": datetime.utcnow()}})
        if token_data:
            return AccessToken(**token_data)
        else:
            return None

    except JWTError:
        # Token decoding failed, indicating an invalid token
        return None

