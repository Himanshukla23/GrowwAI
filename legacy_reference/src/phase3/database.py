import sqlite3
import pandas as pd
from pathlib import Path
from .config import settings

def _get_connection() -> sqlite3.Connection:
    path = Path(settings.DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    # Removed conn.row_factory = sqlite3.Row because Pandas bugs out and casts SQLite integers to BLOBs
    return conn

def init_db() -> None:
    """Initialize SQLite database with required tables."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                cuisine TEXT NOT NULL,
                avg_cost INTEGER NOT NULL,
                rating REAL NOT NULL,
                cost TEXT NOT NULL,
                UNIQUE(name, location)
            )
        """)
        # Index for fast filtering
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_location_cuisine ON restaurants(location, cuisine)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rating_cost ON restaurants(rating, cost)")
        conn.commit()

def upsert_restaurants(df: pd.DataFrame) -> None:
    """Bulk insert or replace restaurants from DataFrame."""
    if df.empty:
        return
        
    init_db()
    
    # Convert DataFrame to list of tuples
    raw_records = df[["name", "location", "cuisine", "avg_cost", "rating", "cost"]].to_records(index=False)
    # Ensure native types instead of numpy scalar types (which SQlite saves as BLOBs)
    records = [
        (str(row[0]), str(row[1]), str(row[2]), int(row[3]), float(row[4]), str(row[5]))
        for row in raw_records
    ]
    
    with _get_connection() as conn:
        cursor = conn.cursor()
        # UPSERT logic using REPLACE (since we have UNIQUE constraint on name, location)
        cursor.executemany("""
            REPLACE INTO restaurants (name, location, cuisine, avg_cost, rating, cost)
            VALUES (?, ?, ?, ?, ?, ?)
        """, records)
        conn.commit()

def get_all_restaurants() -> pd.DataFrame:
    """Read all restaurants natively via SQL instead of CSV load."""
    init_db()  # Ensure DB exists
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, location, cuisine, avg_cost, rating, cost FROM restaurants")
        rows = cursor.fetchall()
        
        # Manually decode in case SQLite fetched raw memory buffers due to to_records anomalies
        decoded_rows = []
        for row in rows:
            name, loc, cuisine, avg_cost, rating, cost = row
            if isinstance(avg_cost, bytes):
                avg_cost = int.from_bytes(avg_cost, "little")
            if isinstance(rating, bytes):
                import struct
                rating = struct.unpack('d', rating)[0]
                
            decoded_rows.append({
                "name": name,
                "location": loc,
                "cuisine": cuisine,
                "avg_cost": int(avg_cost) if avg_cost else 0,
                "rating": float(rating) if rating else 0.0,
                "cost": cost
            })
            
        df = pd.DataFrame(decoded_rows)
    return df

def get_stats() -> dict:
    """Get database stats for health checks."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM restaurants")
            count = cursor.fetchone()[0]
            cursor.execute("SELECT MAX(rating), AVG(avg_cost) FROM restaurants")
            max_rating, avg_cost = cursor.fetchone()
            
            return {
                "status": "online",
                "record_count": count,
                "db_path": settings.DB_PATH,
                "max_rating": max_rating or 0,
                "avg_overall_cost": round(avg_cost or 0, 2)
            }
    except Exception as e:
        return {"status": "offline", "error": str(e)}

def get_unique_locations(query: str = "") -> list[str]:
    """Return distinct locations, optionally filtered by partial match."""
    init_db()
    with _get_connection() as conn:
        cursor = conn.cursor()
        if query:
            cursor.execute(
                "SELECT DISTINCT location FROM restaurants WHERE location LIKE ? ORDER BY location LIMIT 20",
                (f"%{query.lower()}%",)
            )
        else:
            cursor.execute("SELECT DISTINCT location FROM restaurants ORDER BY location")
        return [row[0] for row in cursor.fetchall()]

def get_unique_cuisines(query: str = "") -> list[str]:
    """Return distinct individual cuisines, optionally filtered by partial match.
    Cuisines in the DB are often comma-separated (e.g. 'north indian, chinese'),
    so we split and deduplicate them."""
    init_db()
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT cuisine FROM restaurants")
        raw = [row[0] for row in cursor.fetchall()]
    
    # Explode comma-separated cuisines into individual items
    unique = set()
    for entry in raw:
        for part in entry.split(","):
            cleaned = part.strip().lower()
            if cleaned:
                unique.add(cleaned)
    
    # Sort and optionally filter
    result = sorted(unique)
    if query:
        q = query.lower()
        result = [c for c in result if q in c]
    return result[:50]

# Auto-initialize on import
init_db()
