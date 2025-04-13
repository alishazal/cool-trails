import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from pybars import Compiler
import models, database, domain

app = FastAPI()

# Create DB tables if they don't exist
models.Base.metadata.create_all(bind=database.engine)

# Mount static files (CSS, images, etc.)
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Helper function to load and render a Handlebars template
def render_template(template_name: str, context: dict = {}) -> str:
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    template_path = os.path.join(templates_dir, template_name)
    with open(template_path, "r", encoding="utf-8") as file:
        source = file.read()
    compiler = Compiler()
    template = compiler.compile(source)
    rendered = template(context)
    return rendered

# Home page: renders home.hbs
@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
def home():
    context = {"message": "Welcome to the Cool Trails!"}
    html_content = render_template("home.hbs", context)
    return HTMLResponse(content=html_content)

# Search page: runs a SQL query and renders search.hbs
@app.get("/search", response_class=HTMLResponse)
def search(q: str = ""):
    trails = domain.search_trails(q)
    context = {"trails": trails}
    html_content = render_template("search.hbs", context)
    return HTMLResponse(content=html_content)

# Trail info page: loads details via SQL and renders trail.hbs
@app.get("/trail/{trail_id}", response_class=HTMLResponse)
def trail_detail(trail_id: int):
    trail_dict, center = domain.get_trail_info(trail_id)
    if not trail_dict:
        raise HTTPException(status_code=404, detail="Trail not found")
    context = {"trail": trail_dict, "center": center}
    html_content = render_template("trail.hbs", context)
    return HTMLResponse(content=html_content)

# Add test trail
@app.post("/trail/add-test", response_class=HTMLResponse)
def add_test_trail(
    name: str = "Test Trail",
    location: str = "Los Angeles, CA",
    description: str = "A sample trail added via API for testing."
):
    new_trail = domain.add_test_trail(name, location, description)
    return f"Added Trail with ID {new_trail.id}"
