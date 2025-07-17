from fastapi import FastAPI

def ping_route(app:FastAPI):
    @app.get("/")
    def ping_route():
        return {"message": "Backend online."}