from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """What the client sends when creating a new account."""
    name: str
    email: EmailStr
    password: str  # plain text from the user — gets hashed before storage, never stored as-is


class UserLogin(BaseModel):
    """What the client sends when logging in."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """What the server sends back after successful register/login."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str