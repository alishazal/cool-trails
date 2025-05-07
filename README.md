<div align="center" width="100%">
    <img src="static/logo_light.svg" width="400" alt="" />
</div>

# Cool Trails 🥾

<!-- ▼▼▼▼ Uncomment these if the Repo is made public ▼▼▼▼ -->

 <!-- <a target="_blank" href="https://github.com/alishazal/cool-trails"><img src="https://img.shields.io/github/stars/alishazal/cool-trails?style=flat" /></a>  -->
<!-- <a target="_blank" href="https://github.com/rlmoore-b/cool-trails"><img src="https://img.shields.io/github/last-commitalishazal/cool-trails" ></a> -->
<!-- <a href="https://github.com/rlmoore-b/cool-trails"><img src="https://hits.sh/github.com/alishazal/cool-trails.svg?style=flat-square&label=%20Views&color=purple" alt="Views" /></a> -->

<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python" /></a>
<img src="https://img.shields.io/badge/Handlebars%20js-f0772b?style=for-the-badge&logo=handlebarsdotjs&logoColor=black" alt="Handlebars" /><a>
<img src="https://img.shields.io/badge/Sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" /></a>
<img src="https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap" /></a>
<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS" /></a>
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML" /></a>
<img src="https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E" alt="JavaScript" /></a>
<img src="https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white" alt="FastAPI" /></a>

Check out our live site: [cool-trails.com](https://cool-trails.com)

Cool trails is an intuitve app to help all hikers from beginner to expert prepare for their upcoming adventure. It provides gear recommendations based on trail conditions, and shows users the shaded and sunny parts of any trail. 

<img src="images/Demo Image.png" width="750" alt="" />

## Tech Stack
- BE: Python with FastAPI
- FE: Handlebars, Boostrap, CSS, HTML, JS
- DB: SQLite

## Getting Started
1. Initialize a venv or conda environment. In VSCode you can do this by doing ```cmd + shift + P```, then select "Python: Create Environment", then select "Venv", and finally select your Python version.
2. Run ```brew install geos``` in terminal to install GEOS which is required to install Shapely (one of the Python libraries we're using).
3. Run ```pip install -r requirements.txt``` in terminal to install all required Python libraries in the env.
4. To run the app, run the following in terminal at the root directory of this project: ```uvicorn api.main:app --reload```
5. The app will be running on ```http://localhost:8000/``` or check the logs in the terminal to see which port its running on.
6. [Do this only once - it downloads a 1.2 GB file] Next, download the california trails data by running ```sh scripts/download_data.sh``` in terminal at the root directory.
7. Insert the trails from the file to the database. Run ```python -m scripts.ingest_ca_trails_adv``` in terminal at the root directory. This script takes around 10 minutes to run.
8. Then merge broken trails (openstreetmap breaks trails due to varying surfaces, so we're gonna stitch segments together to form full trails). Run ```python -m scripts.merge_segments```. This script also takes around 10 minutes to run.
9. Now create the FTS5 table for autocomplete suggestions. First open the database by running the following in terminal: ```sqlite3 trails.db```. Once you're in sqlite's cli, run the following:
```
CREATE VIRTUAL TABLE IF NOT EXISTS trails_fts
USING fts5(
  name, 
  description,
  content='trails',           -- link to your real table
  content_rowid='id'          -- use the same PK
);
```
Then run the following (takes a couple of minutes):
```
INSERT INTO trails_fts(rowid, name, description)
  SELECT id, name, description FROM trails;
```

## Usage

#### Swagger API Docs
All endpoints can be tested by visiting ```http://localhost:8000/docs```. This is powered by Swagger, which comes with FastAPI, for building automatic api docs.

#### Endpoints / Pages
The following endpoints are accessible through the browser
- /home
- /search
- /trail/{trail_id}

#### Database
To access the database do the following:
1. Run the app by following the Getting Started instructions.
2. In your terminal in the root directory run this command: ```sqlite3 trails.db```
3. Now you should be in the database file. You can run commands like ```.tables``` or any other sql commands to check out the available tables, etc.

If you make changes to the database schema, delete the trails.db file and run the server again to have a new trails.db file created.

## Created By

- [Ali Shazal](https://github.com/alishazal)
- [Brevin Smider](https://github.com/bsmider)
- [Robert Moore](https://github.com/rlmoore-b)
- [Franco Lopez](https://github.com/FrancoLopezDev)