from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemRead(BaseModel):
    id: int
    name: str
    description: str
    file_path: str

    class Config:
        from_attributes = True


class CollectionCreate(BaseModel):
    name: str
    description: str


class CollectionRead(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: str


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True


class InstanceCreate(BaseModel):
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

    class Config:
        from_attributes = True
