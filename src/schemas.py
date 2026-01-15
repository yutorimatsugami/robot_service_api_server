from pydantic import BaseModel
from typing import Optional, List

# Ad/Shop Schemas
class AdContentBase(BaseModel):
    shop_name: str
    category: Optional[str] = None
    description: Optional[str] = None
    business_hours: Optional[str] = None

class AdContent(AdContentBase):
    ad_id: int
    file_path: Optional[str] = None
    map_node_id: Optional[int] = None

    class Config:
        from_attributes = True

# Chat Schemas
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "guest"

class ChatResponse(BaseModel):
    response: str
    related_ads: Optional[List[AdContent]] = []
