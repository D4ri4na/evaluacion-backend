from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os

password = os.getenv("POSTGRES_PASSWORD")
app = FastAPI(title="Tickets API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database=os.getenv("POSTGRES_DB", "tickets_database"),
            user=os.getenv("POSTGRES_USER", "app"),
            password=os.getenv("POSTGRES_PASSWORD") # Esta variable ya la definiste arriba
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

@app.get("/v1/healthz")
def health_check():
    db_conn = get_db_connection()
    if db_conn:
        db_conn.close()
        return {"status": "ok"}
    raise HTTPException(status_code=503, detail="Database unhealthy")

def fetch_shows_from_database():
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT 
            e.id, 
            e.title, 
            e.event_date AS starts_at, 
            e.description,
            v.name AS venue_name,
            v.city AS venue_city
        FROM content.event e
        INNER JOIN content.venue v ON e.venue_id = v.id
        ORDER BY e.event_date ASC;
    """)
    events = cur.fetchall()
    
    results = []
    for event in events:
        if event['starts_at']:
            event['starts_at'] = event['starts_at'].isoformat()
            
        # Reestructuramos el objeto venue tal como lo pide tu app.js
        event['venue'] = {
            "name": event.pop('venue_name'),
            "city": event.pop('venue_city')
        }
        
        cur.execute("""
            SELECT 
                COALESCE(MIN(price), 0) as min_price,
                COALESCE(SUM(available_quantity), 0) as available,
                COALESCE(SUM(total_capacity), 0) as total_capacity
            FROM content.ticket_tier
            WHERE event_id = %s;
        """, (event['id'],))
        
        agg = cur.fetchone()
        event['min_price'] = float(agg['min_price']) if agg['min_price'] else 0.0
        event['available'] = int(agg['available'])
        event['total_capacity'] = int(agg['total_capacity'])
        
        results.append(event)
        
    cur.close()
    conn.close()
    return results

@app.get("/v1/events/")
def list_events(page: int = 1, page_size: int = 9):
    results = fetch_shows_from_database()
    return {
        "count": len(results),
        "page": page,
        "results": results
    }

@app.get("/v1/events/{event_id}")
def get_event_detail(event_id: str):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT e.id, e.title, e.event_date AS starts_at, e.description,
               v.name AS venue_name, v.city AS venue_city
        FROM content.event e
        INNER JOIN content.venue v ON e.venue_id = v.id
        WHERE e.id = %s;
    """, (event_id,))
    event = cur.fetchone()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if event['starts_at']:
        event['starts_at'] = event['starts_at'].isoformat()
        
    event['venue'] = {
        "name": event.pop('venue_name'),
        "city": event.pop('venue_city')
    }
    
    cur.execute("""
        SELECT name, price, available_quantity AS available 
        FROM content.ticket_tier 
        WHERE event_id = %s;
    """, (event_id,))
    tiers = cur.fetchall()
    
    for t in tiers:
        t['price'] = float(t['price'])
        
    event['tiers'] = tiers
    
    cur.close()
    conn.close()
    return event