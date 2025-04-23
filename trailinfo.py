from fastapi import FastAPI

trailinfo = FastAPI()


class Base(DeclarativeBase):
    pass

# TODO: refactor, placeholder
class TrailInfo(Base):
    __tablename__ = 'TrailInfo'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String)
    terrain: Mapped[str | None] = mapped_column(String)
    difficulty: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=2, scale=1), # e.g., stores up to 10 digits total, 2 after the decimal
        nullable=True # Allow null values for difficulty
    )

    def __repr__(self):
        # Optional: How the object prints
        return f"<Item(id={self.id}, name='{self.name}')>"

@trailinfo.get("/")
async def getTrailInfo(trail_id):
    # TODO: get trail info from DB and return it
    pass

@trailinfo.post("/")
async def addTrailInfo(trail_id):
    # TODO: add trail info to the DB
    pass

@trailinfo.put("/")
async def addTrailInfo(trail_id):
    # TODO: update trail info in the DB
    pass

@trailinfo.delete("/")
async def addTrailInfo(trail_id):
    # TODO: delete trail info in the DB
    pass


