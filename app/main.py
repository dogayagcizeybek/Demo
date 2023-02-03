from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from app.local_settings import postgresql as settings
from app.api.api_v1.api import router as api_router

app = FastAPI()

class UpdatePerson(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    

def get_engine(user, passwd, host, port, db):
    print(f"postgresql://{user}:{passwd}@{host}:{port}/{db}")
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
     
    engine = create_engine(url, pool_size=50, echo=False)
    print(engine.url)
    if not database_exists(engine.url):
        print("database yok")
        create_database(engine.url)
    print("database var")    
        
    

    return engine

def get_engine_from_settings(settings):
    keys = ["pguser", "pgpasswd", "pghost", "pgport", "pgdb"]
    if not all(key in keys for key in settings.keys()):
        raise Exception("Bad config file")
    return get_engine(settings["pguser"], settings["pgpasswd"], settings["pghost"], settings["pgport"], settings["pgdb"])

engine = get_engine_from_settings(settings)

def get_session(settings, engine):
    engine = get_engine_from_settings(settings)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

session = get_session(settings, engine)
 
def provide_people(engine):

    session.execute(text("""
    CREATE TABLE IF NOT EXISTS people ( person_id serial PRIMARY KEY, name VARCHAR(50) NOT NULL, year INT NOT NULL);
    INSERT INTO 
    people (name, year)
    VALUES
    ('insan1',20),
    ('insan2',21),
   ('insan3',22)
    ON CONFLICT DO NOTHING;
    """))
    session.commit()
    result = session.execute(text("SELECT name, year FROM people"))
    i = 0
    result_dict = dict()
    for j in result:
        i += 1
        result_dict[i] = {"name":j[0], "year":j[1]}
    return result_dict


    



json_people = provide_people(engine)


@app.get("/people")
async def people():
    return json_people

@app.get("/people/{person_id}")
async def people_with_id(person_id: int):
    return str(json_people[person_id])

@app.post("/update_people/{person_id}")
async def update_year(person_id: int,year:int):
    json_people[person_id]["year"] = year
        
    session.execute(text("""
                UPDATE people
        SET name = '{}',
            year = {}
        WHERE person_id = {};
                """.format(json_people[person_id]["name"], json_people[person_id]["year"], person_id)))  
    session.commit()
    
    return str(json_people[person_id])


@app.put("/update_people/{person_id}")
async def update_people(person_id: int,person: UpdatePerson):
    json_people[person_id].update(person)
   
 
       
        
    session.execute(text("""
                UPDATE people
        SET name = '{}',
            year = {}
        WHERE person_id = {};
                """.format(json_people[person_id]["name"], json_people[person_id]["year"], person_id)))  
    session.commit()
    
    return str(json_people[person_id])

@app.get("/")
async def root():
    return {"message": "Hello World2!"}

app.include_router(api_router, prefix="/api/v1")
