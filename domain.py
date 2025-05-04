import json
from shapely.geometry import shape
from sqlalchemy import text
import database
from math import radians, sin, cos, sqrt, atan2

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

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in metres
    φ1, φ2 = radians(lat1), radians(lat2)
    Δφ      = radians(lat2 - lat1)
    Δλ      = radians(lon2 - lon1)
    a = sin(Δφ/2)**2 + cos(φ1)*cos(φ2)*sin(Δλ/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def search_trails(q, diff, min_len, maxlen, min_gain, max_gain, userlat, userlng, radius, page, limit):
    with database.engine.connect() as conn:
        offset = (page - 1) * limit
        query = text('''
            SELECT *
            FROM trails
            WHERE name LIKE :q
                AND ((length_m IS NULL) OR (length_m BETWEEN :min_len AND :maxlen))
                {difficulty_clause}
            LIMIT :limit
            OFFSET :offset
        '''.format(
            difficulty_clause = "AND difficulty IN :diff" if diff else "",
        ))
        result = conn.execute(query, {
            "q": f"%{q}%",
            "diff": diff,
            "min_len": min_len,
            "maxlen": maxlen,
            "limit": int(limit),
            "offset": int(offset)
        })
        trails = [dict(row) for row in result]
        if userlat and userlng and radius:
            trails = [
                t for t in trails
                if haversine(t["center_lat"], t["center_lng"], userlat, userlng) <= radius
            ]
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

def parse_description(description_str):
    pairs = description_str.split(";")
    return {
        key.strip(): value.strip().title()
        for pair in pairs if "=" in pair
        for key, value in [pair.split("=", 1)]
    }
