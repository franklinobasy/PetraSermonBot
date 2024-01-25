# test_functions.py
from datetime import datetime, timedelta
from jose import jwt
import pytest
from database.mongodb import users_collection, access_tokens_collection
from database.mongodb.utils import create_user, get_user_by_email, update_user, delete_user, create_access_token, get_access_token, delete_access_token
from database.mongodb.models import UserCreate, TokenCreate, User, AccessToken

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

@pytest.fixture
def sample_user():
    user_data = {"email": "testuser@example.com", "first_name": "Test", "last_name": "User", "picture": "test_url"}
    return create_user(UserCreate(**user_data))

@pytest.fixture
def sample_access_token(sample_user):
    token_create_data = {"user_id": str(sample_user.id), "secret_key": SECRET_KEY, "algorithm": ALGORITHM}
    return create_access_token(TokenCreate(**token_create_data))

def test_create_user():
    user_data = {"email": "testuser@example.com", "first_name": "Test", "last_name": "User", "picture": "test_url"}
    user = create_user(UserCreate(**user_data))
    assert user is not None

def test_get_user_by_email(sample_user):
    user = get_user_by_email(sample_user.email)
    assert user.email == sample_user.email

def test_update_user(sample_user):
    user_update_data = {"first_name": "UpdatedTest", "last_name": "UpdatedUser", "picture": "updated_url"}
    updated_user = update_user(str(sample_user.id), UserCreate(**user_update_data))
    assert updated_user.first_name == user_update_data["first_name"]

def test_delete_user(sample_user):
    result = delete_user(str(sample_user.id))
    assert result is True

def test_create_access_token():
    user_id = "test_user_id"
    token_create_data = {"user_id": user_id, "secret_key": SECRET_KEY, "algorithm": ALGORITHM}
    access_token = create_access_token(TokenCreate(**token_create_data))
    assert access_token is not None

def test_get_access_token(sample_user, sample_access_token):
    access_token = get_access_token(str(sample_user.id))
    assert access_token.access_token == sample_access_token.access_token

def test_delete_access_token(sample_user):
    result = delete_access_token(str(sample_user.id))
    assert result is True