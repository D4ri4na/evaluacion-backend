from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from services.event_service import EventService
from repositories.event_repository import EventRepositoryProtocol, PostgresEventRepository
from cache.rate_limiter import CacheProtocol, get_cache, IPRateLimiter
from schemas import PaginatedEventsSchema, EventDetailSchema

router = APIRouter()
rate_limiter = IPRateLimiter(requests_per_minute=20)

def get_event_repository() -> EventRepositoryProtocol:
    return PostgresEventRepository()

def get_event_service(
    repository: EventRepositoryProtocol = Depends(get_event_repository),
    cache: CacheProtocol = Depends(get_cache)
) -> EventService:
    return EventService(repository, cache)

@router.get("/events/", response_model=PaginatedEventsSchema, dependencies=[Depends(rate_limiter)])
def list_events(
    q: Optional[str] = None,
    page: int = 1, 
    page_size: int = 9, 
    service: EventService = Depends(get_event_service)
):
    return service.list_all_events(search_query=q, page=page, page_size=page_size)

@router.get("/events/{event_id}", response_model=EventDetailSchema, dependencies=[Depends(rate_limiter)])
def get_event_detail(
    event_id: str, 
    service: EventService = Depends(get_event_service)
):
    event = service.get_event_detail(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.get("/events/search/", response_model=PaginatedEventsSchema, dependencies=[Depends(rate_limiter)])
def search_events(
    query: str, 
    page: int = 1, 
    page_size: int = 9, 
    service: EventService = Depends(get_event_service)
):
    return service.list_all_events(search_query=query, page=page, page_size=page_size)

@router.get("/events/upcoming", response_model=PaginatedEventsSchema, dependencies=[Depends(rate_limiter)])
def upcoming_events(
    window: str, 
    tz: str = "UTC", 
    page: int = 1, 
    page_size: int = 9, 
    service: EventService = Depends(get_event_service)
):
    if window not in ["weekend", "week", "month"]:
        raise HTTPException(status_code=400, detail="Window must be 'weekend', 'week', or 'month'")
    
    return service.get_upcoming_events(window=window, tz_name=tz, page=page, page_size=page_size)

