# services/osm.py
import overpy, shapely.geometry as geom
import shapely.ops as ops
from decimal import Decimal

api = overpy.Overpass(max_retry_count=3)

def fetch_trails(bbox: str):
    """
    bbox =  'south,west,north,east'  (decimal degrees)
    returns GeoJSON FeatureCollection (dict)
    """
    q = f"""
      (
        way["highway"="path"]({bbox});
        relation["route"="hiking"]({bbox});
      );
      (._;>;);
      out geom;
    """
    result = api.query(q)

    feats = []
    for w in result.ways:
        coords = [(n.lon, n.lat) for n in w.nodes]
        geom_obj = geom.LineString(coords)
        feats.append({
            "type": "Feature",
            "geometry": geom.mapping(geom_obj),
            "properties": {"osm_id": w.id, "name": w.tags.get("name", "")}
        })
    return {"type": "FeatureCollection", "features": feats}

def fetch_canopy(bbox: str):
    q = f"""
      (
        way["natural"="wood"]({bbox});
        way["landuse"="forest"]({bbox});
      );
      (._;>;);
      out geom;
    """
    r = api.query(q)
    feats = []
    for w in r.ways:
        coords = [
            (float(n.lon), float(n.lat)) 
            for n in w.nodes
        ]
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [coords]},
            "properties": {}
        })
    return {"type": "FeatureCollection", "features": feats}
