from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.user import UserCreate, UserResponse
from backend.crud import user as user_crud
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/users", tags=["users"]) #prefix="/users" means all routes in this router will start with /users, e.g., /users/ for creating a user or listing users. The tags=["users"] is used for API documentation grouping in Swagger UI.


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_crud.create_user(db, user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A user with this email already exists.")

@router.get("/", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_crud.get_users(db, skip, limit)