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

def get_hardcoded_reviews_for_trail(trail_id, trail_name="this trail"):
    return [
        {
            "user_name": "Franco",
            "stars": "⭐⭐⭐⭐⭐",
            "description": f"I loved the views at {trail_name}! Definitely going again"
        },
        {
            "user_name": "Ali",
            "stars": "⭐⭐⭐",
            "description": f"{trail_name} was great, but it got a bit crowded around noon."
        },
        {
            "user_name": "Brevin",
            "stars": "⭐⭐⭐⭐",
            "description": f"Beautiful trail with a lot, of shade!"
        },
        {
            "user_name": "Truong",
            "stars": "⭐⭐⭐⭐⭐",
            "description": f"This was the best trail I've ever done! Absolutely would recommend!"
        },
        {
            "user_name": "Rob",
            "stars": "⭐⭐",
            "description": f"Nice path through {trail_name}. Could use more shade."
        }
    ]

