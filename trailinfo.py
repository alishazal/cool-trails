from fastapi import FastAPI

trailinfo = FastAPI()

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


