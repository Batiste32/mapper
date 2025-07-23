from fastapi import APIRouter, Body, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import httpx
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.database.models import Profile
from backend.utils.geo import get_optimized_route, display_route_on_map
from backend.utils.clustered_geo import *

router = APIRouter()

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    ethnicity: str | None = None
    political_alignment: str | None = None
    min_score_vote: int | None = None

@router.post("/profiles/optimize")
def optimize_profiles(req: RouteRequest = Body(...)):
    """
    - Filter profiles
    - If > 60 points, cluster & multi-batch
    - Else run standard single batch
    - Get real road route
    - Return GeoJSON path
    """

    db = SessionLocal()
    query = db.query(Profile)

    if req.ethnicity:
        query = query.filter(Profile.origin == req.ethnicity)

    if req.political_alignment:
        query = query.filter(Profile.political_lean == req.political_alignment)

    if req.min_score_vote:
        query = query.filter(Profile.score_vote >= req.min_score_vote)

    profiles = query.all()
    db.close()

    if not profiles:
        return {"message": "No matching profiles found."}

    points = []
    profile_ids = []
    profiles_map = {}

    for p in profiles:
        if p.latitude is None or p.longitude is None:
            continue
        points.append((p.latitude, p.longitude))
        profile_ids.append(p.id)
        profiles_map[p.id] = (p.latitude, p.longitude)

    if not points:
        return {"message": "No profiles with valid coordinates."}

    start_coord = (req.start_lat, req.start_lon)

    if len(points) > 30:
        print(f"Large batch: {len(points)} points. Clustering...")
        clusters = cluster_points(points, max_cluster_size=60)
        full_ordered_points, cluster_results = combine_cluster_routes(
            start_coord,
            clusters,
            points,
            profile_ids
        )
        print("Clusters optimized, drawing map...")
        route_geojson = display_clustered_route(full_ordered_points, cluster_results, start_coord=start_coord)
        print(route_geojson)
        return route_geojson
    
    print(f"Small batch: {len(points)} points. Single optimization...")
    result, id_map = get_optimized_route(start_coord[0],start_coord[1],points=points,profile_ids=profile_ids
    )

    # Ordered points
    steps = result["routes"][0]["steps"]
    ordered_points = []
    for step in steps:
        if step["type"] == "job":
            job_id = step["job"]
            profile_id = id_map[job_id]
            ordered_points.append(profiles_map[profile_id])

    print("Drawing map...")
    route_geojson = display_route_on_map(
        result,
        id_map,
        profiles_map,
        start_coord=start_coord
    )
    print(route_geojson)
    return route_geojson

@router.get("/geocode")
async def geocode_address(q: str = Query(..., description="The address to geocode")):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={q}"

    headers = {
        "User-Agent": "YourAppName/1.0 (your@email.com)"  # Nominatim requires a real User-Agent
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data
        except httpx.RequestError as exc:
            return JSONResponse(content={"error": f"Network error: {exc}"}, status_code=500)
        except httpx.HTTPStatusError as exc:
            return JSONResponse(content={"error": f"HTTP error: {exc.response.status_code}"}, status_code=exc.response.status_code)