from backend.database.models import *
from backend.utils.routes import utils_routes, auth_routes, admin_routes, profiles_routes, visits_routes, map_routes
from backend.utils.security import *
from backend.utils.geo import update_profiles_latlon_from_csv, test_map

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os

init_loop=True
while init_loop :
    print("Booting app, select option :")
    match input(
"""1 : list admin accounts
2 : create admin account
3 : remove admin account
4 : rebuild database (long process)
5 : test folium optimized_route
else : start app
->""") :
        case "1" :
            list_admins()
        case "2" :
            create_admin()
            print("Admin created")
        case "3" :
            remove_admin()
            print("Admin removed")
        case "4" :
            try :
                os.remove("backend/database/electoral_app.db")
            except :
                pass
            engine = create_data_base()
            import_data_from_csv(engine)
            unresolved,total = update_profiles_latlon_from_csv(engine)
            print(len(unresolved)," / ",total," missing")
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