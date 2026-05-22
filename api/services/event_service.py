import json
from repositories.event_repository import EventRepositoryProtocol
from cache.rate_limiter import CacheProtocol

class EventService:
    def __init__(self, repository: EventRepositoryProtocol, cache: CacheProtocol):
        self.repository = repository
        self.cache = cache

    def list_all_events(self, search_query: str = None, page: int = 1, page_size: int = 9):
        # 1. Intentar obtener de Caché
        cache_key = f"events:q={search_query}:p={page}:s={page_size}"
        cached_data = self.cache.get_value(cache_key)
        if cached_data:
            return json.loads(cached_data)

        # 2. Si no hay caché, buscar en Repositorio (PostgreSQL)
        raw_events = self.repository.get_all_events(search_query)
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
            
        # Paginación a nivel de lógica de negocio
        total_count = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_results = results[start:end]

        final_response = {
            "count": total_count,
            "page": page,
            "results": paginated_results
        }
        
        # 3. Guardar en Caché por 30 segundos
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