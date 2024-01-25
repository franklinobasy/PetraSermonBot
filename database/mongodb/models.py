from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str = None
    picture: str = None

class User(UserCreate):
    id: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenCreate(BaseModel):
    user_id: str
    secret_key: str
    algorithm: str
    expire_minutes: int = 24 * 60
