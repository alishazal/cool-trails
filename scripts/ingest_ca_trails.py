import osmium, shapely.geometry as geom, shapely.ops as ops, json, re
import models, database

HIGHWAY_RE  = re.compile(r'path|footway|cycleway', re.I)
ROUTE_RE    = re.compile(r'hiking|mtb', re.I)

class TrailHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.session = database.SessionLocal()
        self.counter = 0

    def way(self, w):
        if not (HIGHWAY_RE.search(w.tags.get("highway", "")) or
                ROUTE_RE.search(w.tags.get("route", ""))):
            return

        if len(w.nodes) < 2:
            return

        coords = [(n.lon, n.lat) for n in w.nodes]
        line   = geom.LineString(coords)
        center = list(line.centroid.coords)[0]

        self.counter += 1

        trail = models.Trail(
            osm_id      = w.id,
            name        = w.tags.get("name", f"OSM {w.id}"),
            location    = "California",
            description = "; ".join(f"{t.k}={t.v}" for t in w.tags),
            polygon     = json.dumps(geom.mapping(line)),
            center_lat  = center[1],
            center_lng  = center[0],
        )
        self.session.add(trail)

        if self.counter % 100 == 0:       # flush every 100
            print(f"{self.counter:,} trails")
            self.session.commit()

    def close(self):
        self.session.commit()
        self.session.close()

if __name__ == "__main__":
    handler = TrailHandler()
    handler.apply_file("data/california.osm.pbf", locations=True)
