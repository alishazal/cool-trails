# Cool Trails
Cool trails app 🎉

## Tech Stack
- BE: Python with FastAPI
- FE: Handlebars, Boostrap, CSS, HTML, JS
- DB: SQLite

## Getting Started
1. Initialize a venv or conda environment. In VSCode you can do this by doing ```cmd + shift + P```, then select "Python: Create Environment", then select "Venv", and finally select your Python version.
2. Run ```pip install -r requirements.txt``` in the terminal to install all required libraries in the env.
3. To run the app, run the following in the terminal at the root directory of this project: ```uvicorn main:app --reload```

## Usage

#### Swagger API Docs
All endpoints can be tested by visiting ```http://localhost:8000/docs```. This is powered by Swagger, which comes with FastAPI.

#### Endpoints / Pages
The following endpoints are accessible through the browser
- /home
- /search
- /trail/{trail_id}
- /trail/add-test is a POST api and can be called by the swagger url above to add any test trails.

#### Database
To access the database do the following:
1. Run the app by following the Getting Started instructions.
2. In your terminal in the root directory run this command: ```sqlite3 trails.db```
3. Now you should be in the database file. You can run commands like ```.tables```, ```.scheme trails```, etc to check out the available tables, their schema, and so on.

If you make changes to the database schema, delete the trails.db file and run the server again to have a new trails.db file created.