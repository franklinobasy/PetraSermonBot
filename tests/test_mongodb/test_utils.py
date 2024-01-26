# test_functions.py
from datetime import datetime
import pytest
from database.mongodb import users_collection, access_tokens_collection, JWT_SECRET, JWT_ALGORITHM
from database.mongodb.utils import create_user, get_user_by_email, update_user, delete_user, create_access_token, get_access_token, delete_access_token, validate_access_token
from database.mongodb.models import User, TokenCreate, AccessToken


@pytest.fixture
def sample_user():
    user_data = {"email": "testuser@example.com", "first_name": "Test", "last_name": "User", "picture": "test_url"}
    return create_user(User(**user_data))

@pytest.fixture
def sample_access_token(sample_user):
    token_create_data = {"user_id": sample_user.user_id, "secret_key": JWT_SECRET, "algorithm": JWT_ALGORITHM}
    return create_access_token(TokenCreate(**token_create_data))

def test_create_user():
    user_data = {"email": "testuser@example.com", "first_name": "Test", "last_name": "User", "picture": "test_url"}
    user = create_user(User(**user_data))
    assert user is not None

def test_get_user_by_email(sample_user):
    user = get_user_by_email(sample_user.email)
    assert user.email == sample_user.email

def test_update_user(sample_user):
    user_update_data = {"first_name": "UpdatedTest", "last_name": "UpdatedUser", "picture": "updated_url"}
    updated_user = update_user(str(sample_user.user_id), user_update_data)
    assert updated_user.first_name == user_update_data["first_name"]

def test_delete_user(sample_user):
    result = delete_user(str(sample_user.user_id))
    assert result is True

def test_create_access_token(sample_user):
    token_create_data = {"user_id": sample_user.user_id, "secret_key": JWT_SECRET, "algorithm": JWT_ALGORITHM}
    access_token = create_access_token(TokenCreate(**token_create_data))
    assert access_token is not None

def test_get_access_token(sample_user, sample_access_token):
    access_token = get_access_token(sample_user.user_id)
    assert access_token.access_token == sample_access_token.access_token

def test_delete_access_token(sample_user):
    result = delete_access_token(sample_user.user_id)
    assert result is True

def test_validate_access_token(sample_user):
    # Create a sample access token and insert it into the database
    token_create_data = {"user_id": str(sample_user.user_id), "secret_key": JWT_SECRET, "algorithm": JWT_ALGORITHM}
    access_token = create_access_token(TokenCreate(**token_create_data))
    
    # Ensure the access token is valid
    validated_token = validate_access_token(access_token.access_token)
    
    # Delete from database
    delete_access_token(str(sample_user.user_id))
    
    # Assert that the validation result is not None
    assert validated_token is not None
    
    # Assert that the user_id in the validated token matches the sample user's user_id
    assert validated_token.user_id == str(sample_user.user_id)
    
    # Assert that the token is not expired
    assert validated_token.expires_at > datetime.utcnow()