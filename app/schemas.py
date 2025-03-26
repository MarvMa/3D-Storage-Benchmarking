from pydantic import BaseModel, ConfigDict


class ItemCreate(BaseModel):
    """
    Schema for creating a new item.

    Attributes:
        - name (str): The name of the item.
        - description (str): A brief description of the item.
    """
    name: str
    description: str


class ItemRead(BaseModel):
    """
    Schema for reading an item's details.

    Attributes:
        - id (int): The unique identifier of the item.
        - name (str): The name of the item.
        - description (str): A brief description of the item.
        - file_path (str): The file path where the item's file is stored on the server.
    """
    id: int
    name: str
    description: str
    file_path: str

    model_config = ConfigDict(from_attributes=True)
