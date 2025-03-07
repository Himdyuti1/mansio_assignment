from pydantic import BaseModel
from typing import Optional,List

class PropertyBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    status: Optional[str] = "available"

class PropertyCreate(PropertyBase):
    pass

class PropertyResponse(PropertyBase):
    id: int
    ai_keywords: Optional[str] = None
    stripe_product_id: Optional[str] = None

    class Config:
        orm_mode = True

class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None
    ai_keywords:Optional[str] = None

class PropertyRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: float
    status: str
    ai_keywords: Optional[str] = None
    stripe_product_id: Optional[str] = None

    class Config:
        from_attributes = True