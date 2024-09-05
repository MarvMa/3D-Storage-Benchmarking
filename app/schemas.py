from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemRead(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True
