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
    lang: str = "ja"  # "ja" or "en"

class ChatResponse(BaseModel):
    response: str
    related_ads: Optional[List[AdContent]] = []

# Timetable Schemas
class TimetableBase(BaseModel):
    station_name: str
    osaka_departure_time: str
    osaka_platform: Optional[str] = None
    train_type: Optional[str] = None
    destination: Optional[str] = None
    direction: Optional[str] = None
    arrival_status: Optional[str] = None
    
    class Config:
        from_attributes = True
