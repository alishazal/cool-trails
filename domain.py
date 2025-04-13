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

def search_trails(q):
    with database.engine.connect() as conn:
        query = text("SELECT * FROM trails WHERE name LIKE :q")
        result = conn.execute(query, {"q": f"%{q}%"})
        trails = [dict(row) for row in result]
        return trails

def add_test_trail(name, location, description):
    db = database.SessionLocal()
    try:
        test_polygon = (
            '{"type": "Polygon", "coordinates": [['
            '[-122.42, 37.78], '
            '[-122.41, 37.78], '
            '[-122.41, 37.77], '
            '[-122.42, 37.77], '
            '[-122.42, 37.78]'
            ']]}'
        )
        new_trail = models.Trail(
            name=name,
            location=location,
            description=description,
            polygon=test_polygon
        )
        db.add(new_trail)
        db.commit()
        db.refresh(new_trail)
        return new_trail
    finally:
        db.close()
