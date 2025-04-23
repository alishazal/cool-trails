# scripts/merge_segments.py
import json
from shapely import ops
from shapely.geometry import shape, mapping
from sqlalchemy import select, update
from database import SessionLocal
import models

db = SessionLocal()

names = db.execute(
    select(models.Trail.name).distinct()
).scalars().all()

for nm in names:
    # ---- load GeoJSON as Shapely geometries ----
    geoms = [
        shape(json.loads(t.polygon))
        for t in db.execute(
            select(models.Trail).where(models.Trail.name == nm)
        ).scalars()
    ]
    if len(geoms) < 2:
        continue

    merged = ops.linemerge(ops.unary_union(geoms))

    first_id = db.execute(
        select(models.Trail.id)
        .where(models.Trail.name == nm)
        .limit(1)
    ).scalar_one()

    # ---- store merged geometry back as GeoJSON ----
    db.execute(
        update(models.Trail)
        .where(models.Trail.id == first_id)
        .values(polygon=json.dumps(mapping(merged), separators=(",", ":")))
    )

    # delete the extra duplicate rows
    db.execute(
        models.Trail.__table__.delete()
        .where(models.Trail.name == nm, models.Trail.id != first_id)
    )

db.commit()
db.close()
