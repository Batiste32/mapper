from fastapi import APIRouter, Body, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import and_

import backend.database as db_module
from backend.database.models import Profile
from backend.utils.geo import get_optimized_route, display_route_on_map
from backend.utils.clustered_geo import *

router = APIRouter()

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    filters: Optional[Dict[str, Any]] = None


@router.post("/profiles/optimize")
def optimize_profiles(req: RouteRequest = Body(...)):
    """
    - Accepts arbitrary filters as {field: value}
    - Filter profiles dynamically
    - If > 60 points, cluster & multi-batch
    - Else run standard single batch
    - Get real road route
    - Return GeoJSON path
    """

    db = db_module.SessionLocal()
    query = db.query(Profile)

    # Apply filters dynamically
    if req.filters:
        print(f"Filtering database on : {req.filters}")
        filter_clauses = []
        for field, value in req.filters.items():
            if not hasattr(Profile, field):
                raise HTTPException(status_code=400, detail=f"Invalid field: {field}")

            col = getattr(Profile, field)

            if isinstance(value, dict):
                if "gte" in value:
                    filter_clauses.append(col >= value["gte"])
                if "lte" in value:
                    filter_clauses.append(col <= value["lte"])
                if "eq" in value:
                    filter_clauses.append(col == value["eq"])
            else:
                filter_clauses.append(col == value)
        
        if filter_clauses:
            query = query.filter(and_(*filter_clauses))

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

    # Clustering vs single batch
    if len(points) > 30:
        clusters = cluster_points(points, max_cluster_size=50)
        full_ordered_points, cluster_results = combine_cluster_routes(
            start_coord,
            clusters,
            points,
            profile_ids
        )
        route_geojson = display_clustered_route(
            full_ordered_points, cluster_results, start_coord=start_coord
        )
        return route_geojson

    result, id_map = get_optimized_route(
        start_coord[0], start_coord[1], points=points, profile_ids=profile_ids
    )

    # reconstruct ordered points
    steps = result["routes"][0]["steps"]
    ordered_points = []
    for step in steps:
        if step["type"] == "job":
            job_id = step["job"]
            profile_id = id_map[job_id]
            ordered_points.append(profiles_map[profile_id])

    route_geojson = display_route_on_map(
        result,
        id_map,
        profiles_map,
        start_coord=start_coord
    )
    return route_geojson


@router.get("/geocode")
async def geocode_address(q: str = Query(..., description="The address to geocode")):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={q}"
    headers = {
        "User-Agent": "YourAppName/1.0 (your@email.com)"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            return JSONResponse(content={"error": f"Network error: {exc}"}, status_code=500)
        except httpx.HTTPStatusError as exc:
            return JSONResponse(content={"error": f"HTTP error: {exc.response.status_code}"}, status_code=exc.response.status_code)
