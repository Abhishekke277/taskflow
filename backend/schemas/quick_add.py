from pydantic import BaseModel


class QuickAddRequest(BaseModel):
    """Free-text task description sent by the client, per Section 3.""" # """ this is a docstring that describes the purpose of the QuickAddRequest class. It indicates that this class is used to represent a free-text task description sent by the client, as specified in Section 3 of the requirements or documentation. """
    description: str
    project_id: int