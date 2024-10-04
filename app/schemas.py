from typing import Optional, List

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


class CollectionCreate(BaseModel):
    """
    Schema for creating a new collection.

    Attributes:
        - name (str): The name of the collection.
        - description (str): A brief description of the collection.
    """
    name: str
    description: str
    item_ids: Optional[List[int]] = None  # List of item IDs to associate with the collection


class CollectionRead(BaseModel):
    """
    Schema for reading a collection's details.

    Attributes:
        - id (int): The unique identifier of the collection.
        - name (str): The name of the collection.
        - description (str): A brief description of the collection.
    id: int
    name: str
    description: str
    items: Optional[List[int]] = None  # List of associated item IDs

    model_config = ConfigDict(from_attributes=True)
     """
    id: int
    name: str
    description: str
    items: Optional[List[int]] = None  # List of associated item IDs

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    """
    Schema for creating a new project.

    Attributes:
        - name (str): The name of the project.
        - description (str): A brief description of the project.
    """
    name: str
    description: str


class ProjectRead(BaseModel):
    """
    Schema for reading a project's details.

    Attributes:
        - id (int): The unique identifier of the project.
        - name (str): The name of the project.
        - description (str): A brief description of the project.
        - qr_code_url (str): The URL where the project's QR code can be accessed.
    """
    id: int
    name: str
    description: str
    qr_code_url: str

    model_config = ConfigDict(from_attributes=True)


class InstanceCreate(BaseModel):
    """
    Schema for creating a new instance of a 3D object within a project.

    Attributes:
        - project_id (int): The ID of the project to which this instance belongs.
        - item_id (int): The ID of the item (3D object) being instantiated.
        - position_x (float): The X-coordinate for the position of the instance.
        - position_y (float): The Y-coordinate for the position of the instance.
        - position_z (float): The Z-coordinate for the position of the instance.
        - rotation_x (float): The rotation around the X-axis for the instance.
        - rotation_y (float): The rotation around the Y-axis for the instance.
        - rotation_z (float): The rotation around the Z-axis for the instance.
        - scale_x (float): The scaling factor along the X-axis for the instance.
        - scale_y (float): The scaling factor along the Y-axis for the instance.
        - scale_z (float): The scaling factor along the Z-axis for the instance.
    """
    project_id: int
    item_id: int
    position_x: float
    position_y: float
    position_z: float
    rotation_x: float
    rotation_y: float
    rotation_z: float
    scale_x: float
    scale_y: float
    scale_z: float


class InstanceRead(BaseModel):
    """
    Schema for reading the details of an instance of a 3D object.

    Attributes:
        - id (int): The unique identifier of the instance.
        - project_id (int): The ID of the project to which this instance belongs.
        - item_id (int): The ID of the item (3D object) being instantiated.
        - position_x (float): The X-coordinate for the position of the instance.
        - position_y (float): The Y-coordinate for the position of the instance.
        - position_z (float): The Z-coordinate for the position of the instance.
        - rotation_x (float): The rotation around the X-axis for the instance.
        - rotation_y (float): The rotation around the Y-axis for the instance.
        - rotation_z (float): The rotation around the Z-axis for the instance.
        - scale_x (float): The scaling factor along the X-axis for the instance.
        - scale_y (float): The scaling factor along the Y-axis for the instance.
        - scale_z (float): The scaling factor along the Z-axis for the instance.
    """
    id: int
    project_id: int
    item_id: int
    position_x: float
    position_y: float
    position_z: float
    rotation_x: float
    rotation_y: float
    rotation_z: float
    scale_x: float
    scale_y: float
    scale_z: float

    model_config = ConfigDict(from_attributes=True)
