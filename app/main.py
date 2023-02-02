from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from app.local_settings import postgresql as settings
from app.api.api_v1.api import router as api_router

app = FastAPI()

try:
    def get_engine(user, passwd, host, port, db):
        print(f"postgresql://{user}:{passwd}@{host}:{port}/{db}")
        url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    
        if not database_exists(url):
            create_database(url)
        engine = create_engine(url, pool_size=50, echo=False)
        return engine


    def get_engine_from_settings(settings):
        keys = ["pguser", "pgpasswd", "pghost", "pgport", "pgdb"]
        if not all(key in keys for key in settings.keys()):
            raise Exception("Bad config file")
        return get_engine(settings["pguser"], settings["pgpasswd"], settings["pghost"], settings["pgport"], settings["pgdb"])

    def provide_people(engine):
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name, year FROM people"))
        i = 0   
        result_dict = dict()    
        for j in result.mappings():
            i += 1
            result_dict[i] = j
        return result_dict    
    engine = get_engine_from_settings(settings)

    json_people = provide_people(engine)
        

        

    @app.get("/people")
    async def people():
        return json_people

    @app.get("/people/{person_id}")
    async def people_with_id(person_id: int):
        return json_people[person_id]

except:
    print("selam")
    
@app.get("/")
async def root():
    return {"message": "Hello World2!"}

app.include_router(api_router, prefix="/api/v1")
