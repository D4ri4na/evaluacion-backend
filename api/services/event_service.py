import json
import zoneinfo
from datetime import datetime, timedelta
from repositories.event_repository import EventRepositoryProtocol
from cache.rate_limiter import CacheProtocol

class EventService:
    def __init__(self, repository: EventRepositoryProtocol, cache: CacheProtocol):
        self.repository = repository
        self.cache = cache

    def _process_event_list(self, raw_events, page, page_size):
        if not raw_events:
            return {"count": 0, "page": page, "results": []}

        results = []
        for event in raw_events:
            if event.get('starts_at'):
                event['starts_at'] = event['starts_at'].isoformat()
            
            event['venue'] = {
                "name": event.pop('venue_name', ''),
                "city": event.pop('venue_city', '')
            }
            
            agg = self.repository.get_aggregated_tier_data(event['id'])
            event['min_price'] = float(agg['min_price']) if agg and agg.get('min_price') else 0.0
            event['available'] = int(agg['available']) if agg else 0
            event['total_capacity'] = int(agg['total_capacity']) if agg else 0
            
            results.append(event)
            
        total_count = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        
        return {
            "count": total_count,
            "page": page,
            "results": results[start:end]
        }

    def list_all_events(self, search_query: str = None, page: int = 1, page_size: int = 9):
        cache_key = f"events:q={search_query}:p={page}:s={page_size}"
        cached_data = self.cache.get_value(cache_key)
        if cached_data: return json.loads(cached_data)

        raw_events = self.repository.get_all_events(search_query)
        final_response = self._process_event_list(raw_events, page, page_size)
        
        self.cache.set_value(cache_key, json.dumps(final_response), 30)
        return final_response

    def get_upcoming_events(self, window: str, tz_name: str, page: int = 1, page_size: int = 9):
        try:
            user_tz = zoneinfo.ZoneInfo(tz_name)
        except zoneinfo.ZoneInfoNotFoundError:
            user_tz = zoneinfo.ZoneInfo("UTC")

        now = datetime.now(user_tz)

        if window == "weekend":
            weekday = now.weekday() 
            if weekday < 4 or (weekday == 4 and now.hour < 18):
                days_to_friday = 4 - weekday
                start_date = now.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=days_to_friday)
            else:
                start_date = now
            days_to_monday = 7 - weekday
            end_date = (now + timedelta(days=days_to_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif window == "week":
            start_date = now
            end_date = now + timedelta(days=7)
        elif window == "month":
            start_date = now
            end_date = now + timedelta(days=30)
        else:
            return {"count": 0, "page": page, "results": []}

        cache_key = f"events:upcoming:{window}:{tz_name}:{page}:{page_size}"
        cached_data = self.cache.get_value(cache_key)
        if cached_data: return json.loads(cached_data)

        raw_events = self.repository.get_all_events(start_date=start_date, end_date=end_date)
        final_response = self._process_event_list(raw_events, page, page_size)

        self.cache.set_value(cache_key, json.dumps(final_response), 30)
        return final_response

    def get_event_detail(self, event_id: str):
        cache_key = f"event:{event_id}"
        cached_data = self.cache.get_value(cache_key)
        if cached_data:
            return json.loads(cached_data)

        event = self.repository.get_event_by_id(event_id)
        if not event:
            return None
            
        if event.get('starts_at'):
            event['starts_at'] = event['starts_at'].isoformat()
            
        event['venue'] = {
            "name": event.pop('venue_name', ''),
            "city": event.pop('venue_city', '')
        }
        
        tiers = self.repository.get_ticket_tiers_for_event(event_id)
        if tiers:
            for t in tiers:
                t['price'] = float(t['price'])
        
        event['tiers'] = tiers or []
        
        self.cache.set_value(cache_key, json.dumps(event), 30)
        return event