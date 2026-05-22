from typing import Protocol, List, Dict, Any, Optional
from psycopg2.extras import RealDictCursor
from database import get_db_connection

class EventRepositoryProtocol(Protocol):
    def get_all_events(self, search_query: Optional[str] = None) -> List[Dict[str, Any]]: ...
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]: ...
    def get_ticket_tiers_for_event(self, event_id: str) -> List[Dict[str, Any]]: ...
    def get_aggregated_tier_data(self, event_id: str) -> Optional[Dict[str, Any]]: ...

class PostgresEventRepository:
    def get_all_events(self, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        if not conn: return []
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT e.id, e.title, e.event_date AS starts_at, e.description,
                       v.name AS venue_name, v.city AS venue_city
                FROM content.event e
                INNER JOIN content.venue v ON e.venue_id = v.id
            """
            params = []
            
            if search_query:
                query += " WHERE e.title ILIKE %s OR e.description ILIKE %s OR v.name ILIKE %s"
                term = f"%{search_query}%"
                params.extend([term, term, term])
                
            query += " ORDER BY e.event_date ASC;"
            
            cur.execute(query, params)
            events = cur.fetchall()
            cur.close()
            return events
        finally:
            conn.close()

    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        if not conn: return None
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT e.id, e.title, e.event_date AS starts_at, e.description,
                       v.name AS venue_name, v.city AS venue_city
                FROM content.event e
                INNER JOIN content.venue v ON e.venue_id = v.id
                WHERE e.id = %s;
            """, (event_id,))
            event = cur.fetchone()
            cur.close()
            return dict(event) if event else None
        finally:
            conn.close()

    def get_ticket_tiers_for_event(self, event_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        if not conn: return []
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT name, price, available_quantity AS available 
                FROM content.ticket_tier 
                WHERE event_id = %s;
            """, (event_id,))
            tiers = cur.fetchall()
            cur.close()
            return [dict(t) for t in tiers]
        finally:
            conn.close()

    def get_aggregated_tier_data(self, event_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        if not conn: return None
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT 
                    COALESCE(MIN(price), 0) as min_price,
                    COALESCE(SUM(available_quantity), 0) as available,
                    COALESCE(SUM(total_capacity), 0) as total_capacity
                FROM content.ticket_tier
                WHERE event_id = %s;
            """, (event_id,))
            agg = cur.fetchone()
            cur.close()
            return dict(agg) if agg else None
        finally:
            conn.close()