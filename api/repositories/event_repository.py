from typing import Protocol, List, Dict, Any, Optional
from psycopg2.extras import RealDictCursor
from database import get_db_connection
from datetime import datetime

class EventRepositoryProtocol(Protocol):
    def get_all_events(self, search_query: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, sort: str = "date") -> List[Dict[str, Any]]: ...
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]: ...
    def get_ticket_tiers_for_event(self, event_id: str) -> List[Dict[str, Any]]: ...
    def get_aggregated_tier_data(self, event_id: str) -> Optional[Dict[str, Any]]: ...

class PostgresEventRepository:
    def get_all_events(self, search_query: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, sort: str = "date") -> List[Dict[str, Any]]:
        conn = get_db_connection()
        if not conn: return []
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            params = []
            where_clauses = []

            if search_query:
                where_clauses.append("(e.title ILIKE %s OR e.description ILIKE %s OR v.name ILIKE %s)")
                term = f"%{search_query}%"
                params.extend([term, term, term])

            if start_date and end_date:
                where_clauses.append("(e.event_date >= %s AND e.event_date < %s)")
                params.extend([start_date, end_date])

            query = """
                SELECT e.id, e.title, e.event_date AS starts_at, e.description,
                       v.name AS venue_name, v.city AS venue_city
                FROM content.event e
                INNER JOIN content.venue v ON e.venue_id = v.id
            """
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                
            if sort == "price":
                query += " ORDER BY (SELECT COALESCE(MIN(price), 0) FROM content.ticket_tier WHERE event_id = e.id) ASC;"
            elif sort == "capacity":
                query += " ORDER BY (SELECT COALESCE(SUM(available_quantity), 0) FROM content.ticket_tier WHERE event_id = e.id) DESC;"
            else:
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