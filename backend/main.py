from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.routes import utils_routes, auth_routes, admin_routes, profiles_routes, visits_routes, map_routes

def run_fastapi_app():
    app = FastAPI(title="Electoral Field App API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://mapper-frontend.onrender.com","https://localhost:8000"],
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
    return app

app = run_fastapi_app()