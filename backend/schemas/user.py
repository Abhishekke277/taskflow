from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        # Allows Pydantic to read data directly from SQLAlchemy
        # model instances (ORM objects), not just dicts
        from_attributes = True #means that Pydantic will read data directly from SQLAlchemy model instances (ORM objects), not just dicts. This is useful when you want to return ORM objects from your database queries and have Pydantic automatically convert them into response models.