from typing import Union, List
from pydantic import BaseModel

class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None

class UserBase(BaseModel):
    email: str

class ItemCreate(ItemBase):
    pass

class UserCreate(UserBase):
    password: str

class Item(ItemBase):
    id: int
    owner_id: int
    
    # This Config class is used to provide configurations to Pydantic.
    class Config:
        orm_mode = True

class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True

    # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, 
    # but an ORM model (or any other arbitrary object with attributes).
