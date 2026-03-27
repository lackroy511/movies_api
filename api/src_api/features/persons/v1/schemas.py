from pydantic import BaseModel


class PersonResponse(BaseModel):
    id: str
    full_name: str
