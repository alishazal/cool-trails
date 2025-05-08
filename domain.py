import json
from shapely.geometry import shape
from sqlalchemy import text
import database
from math import radians, sin, cos, sqrt, atan2
from functools import lru_cache
from rapidfuzz import process, fuzz
from datetime import datetime

@lru_cache()
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

def bbox_from_radius(lat, lng, radius_m):
    # 1° of lat ~111 km; lon shrinks by cos(lat)
    dlat = radius_m / 111_000
    dlon = radius_m / (111_000 * cos(radians(lat)))
    return lat - dlat, lat + dlat, lng - dlon, lng + dlon

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in metres
    φ1, φ2 = radians(lat1), radians(lat2)
    Δφ      = radians(lat2 - lat1)
    Δλ      = radians(lon2 - lon1)
    a = sin(Δφ/2)**2 + cos(φ1)*cos(φ2)*sin(Δλ/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

@lru_cache()
def get_all_trails():
    with database.engine.connect() as conn:
        return conn.execute(text("SELECT id, name FROM trails")).fetchall()

@lru_cache()
def search_trails(q, diff, min_len, maxlen, min_gain, max_gain, userlat, userlng, radius, page, limit):
    clauses = []
    params  = { "limit": limit, "offset": (page-1) * limit }
    
    # 1) Full-text search on name+description
    if q:
        # prefix matching: q* 
        clauses.append("trails_fts MATCH :q || '*'")
        params["q"] = q

    # 2) Difficulty filter
    if diff:
        # build placeholders :d0, :d1, …
        ph = ", ".join(f":d{i}" for i in range(len(diff)))
        clauses.append(f"t.difficulty IN ({ph})")
        for i, v in enumerate(diff):
            params[f"d{i}"] = v

    # 3) Length
    clauses.append("t.length_m BETWEEN :min_len AND :maxlen")
    params["min_len"], params["maxlen"] = min_len, maxlen

    # 4) Geographic bbox
    if userlat is not None and userlat and userlng is not None and userlng and radius:
        min_lat, max_lat, min_lng, max_lng = bbox_from_radius(userlat, userlng, radius)
        clauses.append("t.center_lat BETWEEN :min_lat AND :max_lat")
        clauses.append("t.center_lng BETWEEN :min_lng AND :max_lng")
        params.update(min_lat=min_lat, max_lat=max_lat, min_lng=min_lng, max_lng=max_lng)

    where = " AND ".join(clauses) or "1"

    sql = f"""
    SELECT 
      t.*,
      bm25(trails_fts) AS rank_score
    FROM trails t
    JOIN trails_fts 
      ON trails_fts.rowid = t.id
    WHERE {where}
    ORDER BY
      -- first by text relevance (ascending bm25), then by distance if provided
      rank_score ASC
      {", ( (t.center_lat-:ulat)*(t.center_lat-:ulat) + (t.center_lng-:ulng)*(t.center_lng-:ulng) ) ASC"
       if userlat and userlng else ""}
    LIMIT :limit
    OFFSET :offset;
    """
    # if ordering by distance was injected, also bind ulat/ulng
    if userlat is not None and userlng is not None:
        params["ulat"], params["ulng"] = userlat, userlng

    with database.engine.connect() as conn:
        result = conn.execute(text(sql), params)
        trails = [dict(r) for r in result]
    
    # if FTS gave us nothing *and* the user actually typed something, do a quick fuzzy match on trail names
    if not trails and q and page == 1 and not diff and not maxlen != 1e9:
        rows = get_all_trails()
        name_map = {row["name"]: row["id"] for row in rows}

        # find the top N fuzzy matches to q
        matches = process.extract(
            q,
            name_map.keys(),
            scorer=fuzz.WRatio,
            limit=limit
        )
        good = [name for name, score, _ in matches if score >= 60]

        if good:
            # build dynamic IN-list and CASE ordering
            params2 = {"limit": limit}
            in_params = []
            when_clauses = []

            for idx, name in enumerate(good):
                key = f"name_{idx}"
                in_params.append(f":{key}")
                when_clauses.append(f"WHEN :{key} THEN {idx}")
                params2[key] = name

            in_list   = ", ".join(in_params)
            when_sql  = "\n        ".join(when_clauses)
            else_idx  = len(good)

            sql2 = text(f"""
                SELECT *
                FROM trails
                WHERE name IN ({in_list})
                ORDER BY
                CASE name
                    {when_sql}
                    ELSE {else_idx}
                END
                LIMIT :limit
            """)

            with database.engine.connect() as conn:
                rows2 = conn.execute(sql2, params2).fetchall()
            trails = [dict(r) for r in rows2]

    for t in trails:
        diff = t["difficulty"].lower()
        if diff == "easy":
            t["badge_class"] = "bg-success"
        elif diff == "moderate":
            t["badge_class"] = "bg-warning text-dark"
        else:
            t["badge_class"] = "bg-danger"

    return trails

@lru_cache()
def suggest_trails(q, limit):
    sql = text("""
        SELECT name
        FROM trails_fts
        WHERE trails_fts MATCH :prefix || '*'
        ORDER BY bm25(trails_fts) ASC
        LIMIT :limit
    """)
    params = {"prefix": q, "limit": limit}

    with database.engine.connect() as conn:
        rows = conn.execute(sql, params).fetchall()

    # Flatten to a list of strings
    suggestions = [row[0] for row in rows]
    return suggestions

def get_hardcoded_reviews_for_trail(trail_id, trail_name="this trail"):

    def avatar_url(name):
        if name == "Franco":
            return f"https://avatars.githubusercontent.com/u/107090061?v=4"
        if name == "Ali":
            return f"https://avatars.githubusercontent.com/u/32619954?v=4"
        if name == "Rob":
            return f"https://avatars.githubusercontent.com/u/73447567?v=4"
        if name == "Brevin":
            return f"https://media.licdn.com/dms/image/v2/D5603AQFzW7hHY2uvEg/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1730496940461?e=1752105600&v=beta&t=cnjKere7UlarXf-Sf9va0DRhNPdqpmo1a8g1ODzPeAE"
        if name == "Truong":
            return f"https://media.licdn.com/dms/image/v2/D5603AQE_v4HRtoy0XQ/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1692997661681?e=1752105600&v=beta&t=eQexOGF1GjoNyrkE6cSMp330h91UYnC1Y46iirrNXIE"

    def format_date(iso_date):
        try:
            dt = datetime.strptime(iso_date, "%Y-%m-%d")
            return dt.strftime("%B %d, %Y")  # e.g., May 1, 2024
        except:
            return iso_date

    return [
        {
            "user_name": "Franco",
            "profile_img": avatar_url("Franco"),
            "stars": "⭐⭐⭐⭐⭐",
            "description": f"I loved the views at {trail_name}! Definitely going again",
            "date": format_date("2024-05-06")
        },
        {
            "user_name": "Ali",
            "profile_img": avatar_url("Ali"),
            "stars": "⭐⭐⭐",
            "description": f"{trail_name} was great, but it got a bit crowded around noon.",
            "date": format_date("2024-05-03")
        },
        {
            "user_name": "Brevin",
            "profile_img": avatar_url("Brevin"),
            "stars": "⭐⭐⭐⭐",
            "description": f"Beautiful trail with a lot, of shade!",
            "date": format_date("2024-03-17")
        },
        {
            "user_name": "Truong",
            "profile_img": avatar_url("Truong"),
            "stars": "⭐⭐⭐⭐⭐",
            "description": f"This was the best trail I've ever done! Absolutely would recommend!",
            "date": format_date("2023-12-13")
        },
        {
            "user_name": "Rob",
            "profile_img": avatar_url("Rob"),
            "stars": "⭐⭐",
            "description": f"Nice path through {trail_name}. Could use more shade.",
            "date": format_date("2023-11-06")
        }
    ]

def parse_description(description_str):
    pairs = description_str.split(";")
    return {
        key.strip(): value.strip().title()
        for pair in pairs if "=" in pair
        for key, value in [pair.split("=", 1)]
    }
