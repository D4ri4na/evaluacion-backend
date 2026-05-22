from pydantic import BaseModel
from typing import List, Optional

class VenueSchema(BaseModel):
    name: str
    city: str

class TicketTierSchema(BaseModel):
    name: str
    price: float
    available: int

class EventDetailSchema(BaseModel):
    id: str
    title: str
    starts_at: str
    description: Optional[str] = None
    venue: VenueSchema
    min_price: float = 0.0
    available: int = 0
    total_capacity: int = 0
    tiers: Optional[List[TicketTierSchema]] = []

class PaginatedEventsSchema(BaseModel):
    count: int
    page: int
    results: List[EventDetailSchema]
   