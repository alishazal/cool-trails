import json
from shapely.geometry import shape
from sqlalchemy import text
import models, database

def get_trail_info(trail_id):
    with database.engine.connect() as conn:
        query = text("SELECT * FROM trails WHERE id = :id")
        result = conn.execute(query, {"id": trail_id})
        trail = result.fetchone()

        if not trail:
            return {}, {}

        trail_dict = dict(trail)

        center = None
        if trail_dict.get("polygon"):
            try:
                polygon_data = json.loads(trail_dict["polygon"])
                geom = shape(polygon_data)
                centroid = geom.centroid
                center = {"lat": centroid.y, "lng": centroid.x}
                return trail_dict, center
            except Exception as e:
                print("Error computing centroid:", e)

def search_trails(q, page, limit):
    with database.engine.connect() as conn:
        offset = (page - 1) * limit
        query = text('''
            SELECT *
            FROM trails
            WHERE name LIKE :q
            LIMIT :limit
            OFFSET :offset
        ''')
        result = conn.execute(query, {"q": f"%{q}%", "limit": int(limit), "offset": int(offset)})
        trails = [dict(row) for row in result]
        return trails
