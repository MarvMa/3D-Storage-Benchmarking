from pydantic import BaseModel, ConfigDict


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemRead(BaseModel):
    id: int
    name: str
    description: str
    file_path: str

    model_config = ConfigDict(from_attributes=True)


class CollectionCreate(BaseModel):
    name: str
    description: str


class CollectionRead(BaseModel):
    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str
    description: str


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str
    qr_code_url: str

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)
