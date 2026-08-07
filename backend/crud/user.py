from sqlalchemy.orm import Session
from backend.models.user import User
from backend.schemas.user import UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # loads the auto-generated id back onto the object
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of users from the database with pagination.

    Args:
        db (Session): Database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        example: 110 users get first  0->100 for get remaining 10 users get 100->110


    Returns:
        List[User]: List of user objects.
    """
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int):
    """
    Retrieve a user from the database by their ID.

    Args:
        db (Session): Database session.
        user_id (int): ID of the user to retrieve.

    Returns:
        User: User object if found, None otherwise.
    """
    return db.query(User).filter(User.id == user_id).first()