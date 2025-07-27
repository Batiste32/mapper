from backend.database.operations import parse_database_field, import_data_from_csv, reimport_column_from_csv, create_data_base, isolate_stressed_elements_in_field, normalize_string_value, compare_csv_to_db_column
from backend.database.llm_operations import update_database_nationalities, llm_normalize_field_cached
from backend.database.models import Profile
from backend.utils.routes import utils_routes, auth_routes, admin_routes, profiles_routes, visits_routes, map_routes
from backend.utils.security import list_admins, create_admin, remove_admin
from backend.utils.geo import update_profiles_latlon_from_csv, test_map
from backend.utils.constants import CSV_PATH, DATABASE_PATH, DATABASE_URL, VALID_LEANS, VALID_NATIONALITIES

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

import os

init_loop=True
while init_loop :
    print("Booting app, select option :")
    match input(
"""1 : list admin accounts
2 : create admin account
3 : remove admin account
4 : manage database
5 : test folium optimized_route
else : start app
-> """) :
        case "1" :
            list_admins()
        case "2" :
            create_admin()
            print("Admin created")
        case "3" :
            remove_admin()
            print("Admin removed")
        case "4" :
            print("Database management, select option :")
            match input(
"""1 : rebuild database (long process)
2 : rebuild geolocation columns (lat, lon)
3 : reparse string fields (procedural method)
4 : reparse nationality field (LLM method)
5 : check nationality field modifications
else : back to menu
-> """) :
                case "1" :
                    try :
                        os.remove(DATABASE_PATH)
                    except :
                        pass
                    engine = create_data_base(DATABASE_PATH)
                    import_data_from_csv(engine)
                    unresolved,total = update_profiles_latlon_from_csv(engine)
                    print(len(unresolved)," / ",total," missing geocoding")

                case "2" :
                    engine = create_engine(DATABASE_URL)
                    unresolved,total = update_profiles_latlon_from_csv(engine)
                    print(len(unresolved)," / ",total," missing geocoding")

                case "3" :
                    parse_database_field("profiles",["personnality","political_lean","origin"],
                        [isolate_stressed_elements_in_field, 
                         lambda x : normalize_string_value(x,VALID_LEANS,trim_at=3), 
                         lambda x : normalize_string_value(x,VALID_NATIONALITIES)])
                    print("String fields parsed")

                case "4" :
                    engine = create_engine(DATABASE_URL)
                    session = Session(engine)
                    reimport_column_from_csv(CSV_PATH, "ORIGIN", "origin", DATABASE_PATH)
                    normalized = llm_normalize_field_cached(session, "Profile", "origin", VALID_NATIONALITIES, batch_size=2)
                    update_database_nationalities(session, normalized)

                case "5" :
                    engine = create_engine(DATABASE_URL)
                    session = Session(engine)
                    diffs = compare_csv_to_db_column(CSV_PATH,session,Profile,"uniqueid","origin","UNIQUEID","ORIGIN")
                    print("Mismatch on IDs :")
                    for uid, (csv_val, db_val) in diffs.items():
                        print(f"{uid}: CSV='{csv_val}' vs DB='{db_val}'")
                    print(f"Changed {len(diffs.keys())} elements")

                case _ : 
                    print("Returning to menu")
                
        case "5" :
            test_map()
        case _ :
            print("Starting main app")
            init_loop=False

app = FastAPI(title="Electoral Field App API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
utils_routes.ping_route(app)
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(profiles_routes.router)
app.include_router(visits_routes.router)
app.include_router(map_routes.router)