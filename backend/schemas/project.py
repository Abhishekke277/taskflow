from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    # owner_id removed — now taken automatically from the logged-in user's token


class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int

    class Config:
        from_attributes = True