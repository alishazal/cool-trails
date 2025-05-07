import os, urllib.request
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Tuple
from pybars import Compiler

from services.osm import fetch_trails, fetch_canopy
import models, database, domain, llm
from domain import get_hardcoded_reviews_for_trail, get_trail_info, parse_description, suggest_trails

app = FastAPI()

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IS_PROD = os.environ.get("VERCEL")

if IS_PROD:
    DB_PATH = "/tmp/trails.db"
    release_assets_url = "https://github.com/alishazal/cool-trails/releases/download/v1.0.0"
    print("Downloading db file...")
    urllib.request.urlretrieve(f"{release_assets_url}/trails.db", DB_PATH)
    print("Init db...")
    database.init_db()
    
    # for i in range(1, 6):
    #     curr_vid = f"{release_assets_url}/{i}.mp4"
    #     curr_path = f"/tmp/{i}.mp4"
    #     print(f"Downloading video {curr_vid}...")
    #     urllib.request.urlretrieve(curr_vid, curr_path)
else:
    DB_PATH = "./trails.db"
    models.Base.metadata.create_all(bind=database.engine)

# Mount static files (CSS, images, etc.)
static_path = os.path.join(os.path.dirname(__file__), "../static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Helper function to load and render a Handlebars template
def render_template(template_name: str, context: dict = {}) -> str:
    templates_dir = os.path.join(os.path.dirname(__file__), "../templates")
    template_path = os.path.join(templates_dir, template_name)
    with open(template_path, "r", encoding="utf-8") as file:
        source = file.read()
    compiler = Compiler()
    template = compiler.compile(source)
    rendered = template(context)
    return rendered

@app.get("/health")
def health_check():
    exists = os.path.exists(DB_PATH)
    return {
        "db_present": exists,
        "db_size_bytes": os.path.getsize(DB_PATH) if exists else None
    }

# Home page: renders home.hbs
@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
def home():
    context = {
        "videos_path": '/tmp/' if IS_PROD else "/static/videos/"
    }
    html_content = render_template("home.hbs", context)
    return HTMLResponse(content=html_content)

# Search page: runs a SQL query and renders search.hbs
@app.get("/search", response_class=HTMLResponse)
def search(
    q: str = "",
    diff: List[str] = Query(None),
    min_len: Optional[float] = 0,
    maxlen: Optional[float] = 1e9,
    min_gain: Optional[float] = 0,
    max_gain: Optional[float] = 1e9,
    userlat: Optional[str] = None,
    userlng: Optional[str] = None,
    radius: Optional[float] = 1e9,
    page: int = 1,
    limit: int = 10
):
    diff = tuple(diff) if diff else tuple([])
    userlat = float(userlat) if userlat is not None and userlat else userlat
    userlng = float(userlng) if userlng is not None and userlng else userlng
    trails = domain.search_trails(q, diff, min_len, maxlen, min_gain, max_gain, userlat, userlng, radius, page, limit)
    has_prev  = page > 1
    has_next  = len(trails) == limit
    context = {
        "trails": trails,
        "q": q,
        "diff": diff,
        "userlat": userlat,
        "userlng": userlng,
        "maxlen": maxlen if maxlen != 1e9 else 8046.7,
        "radius": radius if radius != 1e9 else 80467,
        "page":      page,
        "prev_page": page - 1,
        "next_page": page + 1,
        "has_prev":  has_prev,
        "has_next":  has_next,
        "limit":     limit,
    }
    html_content = render_template("search.hbs", context)
    return HTMLResponse(content=html_content)

@app.get("/suggest")
def suggest(
    q: str = Query(..., min_length=1, description="Search prefix"),
    limit: int = Query(5, ge=1, le=20, description="Max suggestions")
):
    """
    Return up to `limit` trail names whose name or description
    begins with the prefix `q`, ordered by full‐text relevance.
    """
    suggestions = suggest_trails(q, limit)
    return JSONResponse(suggestions)

# Trail info page: loads details via SQL and renders trail.hbs
@app.get("/trail/{trail_id}", response_class=HTMLResponse)
def trail_detail(trail_id: int, q: str = None):
    trail_dict, center = get_trail_info(trail_id)
    if not trail_dict:
        raise HTTPException(status_code=404, detail="Trail not found")

    trail_name = trail_dict.get("name", "this trail")
    reviews = get_hardcoded_reviews_for_trail(trail_id, trail_name)

    trail_info = parse_description(trail_dict.get("description", ""))

    context = {
        "trail": trail_dict,
        "trail_info": trail_info,
        "center": center,
        "reviews": reviews,
        "q": q,
    }
    html_content = render_template("trail.hbs", context)
    return HTMLResponse(content=html_content)

# Trail info page: loads details via SQL and renders trail.hbs
@app.get("/trail/{trail_id}/packing_recs", response_class=HTMLResponse)
def packing_recs(trail_id: int, llm_input: str):
    resp_json = llm.get_completion_json(llm_input)
    return JSONResponse(content=resp_json)

@app.get("/trails/osm")
def api_trails(bbox: str):
    """
    GET /trails/osm?bbox=34.1,-118.3,34.3,-118.1
    """
    return JSONResponse(fetch_trails(bbox))

@app.get("/canopy/osm")
def api_trails(bbox: str):
    """
    GET /canopy/osm?bbox=34.1,-118.3,34.3,-118.1
    """
    return JSONResponse(fetch_canopy(bbox))
