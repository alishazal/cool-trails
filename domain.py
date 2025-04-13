from sqlalchemy import text
import models, database

def get_trail_info(trail_id):
    with database.engine.connect() as conn:
        query = text("SELECT * FROM trails WHERE id = :id")
        result = conn.execute(query, {"id": trail_id})
        trail = result.fetchone()
        return dict(trail)

def search_trails(q):
    with database.engine.connect() as conn:
        query = text("SELECT * FROM trails WHERE name LIKE :q")
        result = conn.execute(query, {"q": f"%{q}%"})
        trails = [dict(row) for row in result]
        return trails

def add_test_trail(name, location, description, latitude, longitude):
    db = database.SessionLocal()
    try:
        new_trail = models.Trail(
            name=name,
            location=location,
            description=description,
            latitude=latitude,
            longitude=longitude
        )
        db.add(new_trail)
        db.commit()
        db.refresh(new_trail)
        return new_trail
    finally:
        db.close()
