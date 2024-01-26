"""
Module Name: database.mongodb.models

Description:
This module defines Pydantic models for user-related entities, including User, AccessToken, and TokenCreate.

Dependencies:
- datetime: Standard library module for working with dates and times
- timedelta: Standard library module for representing durations
- Optional: Type hint for an optional value
- BaseModel: Base class for Pydantic models
- uuid4: Function to generate UUIDs

Models:
- User (BaseModel):
  - _id (Optional[str]): Optional unique identifier for the user in the database.
  - user_id (str): Unique identifier for the user generated using UUID4.
  - email (str): Email address of the user.
  - first_name (str): First name of the user.
  - last_name (Optional[str]): Last name of the user (optional).
  - picture (Optional[str]): URL to the user's profile picture (optional).

- AccessToken (BaseModel):
  - user_id (str): Identifier for the user associated with the access token.
  - access_token (str): The access token string.
  - token_type (str): Type of the access token, default is "bearer".
  - expires_at (datetime): Expiry date and time of the access token.

- TokenCreate (BaseModel):
  - user_id (str): Identifier for the user for whom the access token is created.
  - secret_key (str): Secret key used for encoding the access token.
  - algorithm (str): Algorithm used for encoding the access token.
  - expires_at (datetime): Expiry date and time of the access token, default is 24 hours from the current time (UTC).

Usage:
- These models are used to represent and validate data related to users, access tokens, and token creation.
- They can be utilized in conjunction with Pydantic for data validation and serialization in the user management module.

Note:
- Ensure that the provided default values for expires_at in TokenCreate suit your application's requirements for token expiration.
"""
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from uuid import uuid4


class User(BaseModel):
    _id: Optional[str] = None
    user_id: str = uuid4().hex
    email: str
    first_name: str
    last_name: Optional[str] = None
    picture: Optional[str] = None

class AccessToken(BaseModel):
    user_id: str
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class TokenCreate(BaseModel):
    user_id: str
    secret_key: str
    algorithm: str
    expires_at: datetime = datetime.utcnow() + timedelta(minutes=24 * 60)
