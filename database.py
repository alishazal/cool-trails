import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file will be created in the root of the project
if os.environ.get("VERCEL") is None:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./trails.db"
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/trails.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    return
    # trails.db is already created; here we're creating the fts table for search
    with engine.connect() as conn:
        conn.execute(text(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS trails_fts
            USING fts5(
              name, 
              description,
              content='trails',
              content_rowid='id'
            );
            """
        ))

        conn.execute(text(
            """
            INSERT OR REPLACE INTO trails_fts(rowid, name, description)
            SELECT id, name, description
              FROM trails;
            """
        ))
