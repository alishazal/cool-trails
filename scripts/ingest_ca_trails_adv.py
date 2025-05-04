import osmium, shapely.geometry as geom, json, re
from pyproj import Geod
import models, database

HIGHWAY = re.compile(r'path|footway|cycleway', re.I)
ROUTE   = re.compile(r'hiking|mtb', re.I)
geod    = Geod(ellps="WGS84")

# --- quick difficulty helper ------------------------------------------
def classify(tags, length_m):
    sac = tags.get("sac_scale", "").lower()
    if sac in {"mountain_hiking", "demanding_mountain_hiking", "alpine_hiking"}:
        level = "hard"
    elif sac in {"hiking"}:
        level = "moderate"
    else:
        level = "easy"

    # incline bumps difficulty
    if re.match(r"(\d+)%", tags.get("incline", "")) and int(re.match(r"(\d+)", tags["incline"]).group(1)) >= 10:
        level = "hard"

    # length‐based fallback
    if   length_m > 12000: level = "hard"
    elif length_m > 5000:  level = "moderate"

    return level
# -----------------------------------------------------------------------

class Handler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.db     = database.SessionLocal()
        self.buffer = []
        self.rows   = 0

    def way(self, w):
        if not (HIGHWAY.search(w.tags.get("highway","")) or ROUTE.search(w.tags.get("route",""))):
            return
        if len(w.nodes) < 2:
            return

        coords  = [(n.lon, n.lat) for n in w.nodes]
        length  = sum(geod.inv(lon1,lat1,lon2,lat2)[2]
                      for (lon1,lat1),(lon2,lat2) in zip(coords, coords[1:]))
        line    = geom.LineString(coords)
        cx, cy  = line.centroid.xy

        loc = (w.tags.get("addr:city") or w.tags.get("addr:state") or "California")

        self.buffer.append(models.Trail(
            osm_id      = w.id,
            name        = w.tags.get("name", f"OSM {w.id}"),
            location    = loc,
            description = "; ".join(f"{t.k}={t.v}" for t in w.tags),
            polygon     = json.dumps(geom.mapping(line), separators=(',',':')),
            center_lat  = cy[0],
            center_lng = cx[0],
            length_m    = round(length,1),
            difficulty  = classify(w.tags, length),
        ))
        self.rows += 1
        if self.rows % 5000 == 0:
            self.flush()

    def flush(self):
        if self.buffer:
            self.db.bulk_save_objects(self.buffer)
            self.db.commit()
            self.buffer.clear()
            print(f"{self.rows:,} trails")

    def close(self):
        self.flush()
        self.db.close()

if __name__ == "__main__":
    Handler().apply_file("data/california.osm.pbf", locations=True)
