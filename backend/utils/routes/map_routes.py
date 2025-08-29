from fastapi import APIRouter, Body, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy import and_
import httpx

import backend.database as db_module
from backend.database.models import Profile
from backend.utils.geo import get_optimized_route, display_route_on_map
from backend.utils.clustered_geo import cluster_points, combine_cluster_routes, display_clustered_route

router = APIRouter()

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    filters: Optional[Dict[str, Any]] = None

@router.post("/profiles/optimize")
def optimize_profiles(req: RouteRequest = Body(...)):
    db = db_module.SessionLocal()
    try:
        query = db.query(Profile)

        # allow synonyms
        alias_map = {
            "ethnicity": "origin",
            "political_alignment": "political_lean",
            "min_score_vote": "score_vote",
        }

        clauses = []
        if req.filters:
            print(f"Filtering database on : {req.filters}")
            for raw_field, raw_value in req.filters.items():
                if raw_value in ("", None):
                    continue
                field = alias_map.get(raw_field, raw_field)
                if not hasattr(Profile, field):
                    raise HTTPException(status_code=400, detail=f"Invalid field: {raw_field}")

                col = getattr(Profile, field)

                if isinstance(raw_value, dict):
                    if "gte" in raw_value and raw_value["gte"] is not None:
                        clauses.append(col >= raw_value["gte"])
                    if "lte" in raw_value and raw_value["lte"] is not None:
                        clauses.append(col <= raw_value["lte"])
                    if "eq" in raw_value and raw_value["eq"] is not None:
                        clauses.append(col == raw_value["eq"])
                else:
                    # special-case score lower-bound
                    if raw_field == "min_score_vote" or field == "score_vote":
                        try:
                            clauses.append(col >= int(raw_value))
                        except (TypeError, ValueError):
                            pass
                    else:
                        pytype = getattr(col.property.columns[0].type, "python_type", str)
                        if pytype in (int, float):
                            clauses.append(col == raw_value)
                        else:
                            clauses.append(col.ilike(f"%{raw_value}%"))

        if clauses:
            query = query.filter(and_(*clauses))

        profiles = query.all()
    finally:
        db.close()

    if not profiles:
        return {"message": "No matching profiles found."}
    elif len(profiles) > 45 :
        profiles = profiles[:45]
        print("Trimmed profiles to 45 points")
    points, profile_ids, profiles_map = [], [], {}
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
        clusters = cluster_points(points, max_cluster_size=50)
        full_ordered_points, cluster_results = combine_cluster_routes(
            start_coord, clusters, points, profile_ids
        )
        route_geojson = display_clustered_route(full_ordered_points, cluster_results, start_coord=start_coord)
    else :
        result, id_map = get_optimized_route(start_coord[0], start_coord[1], points=points, profile_ids=profile_ids)
        route_geojson = display_route_on_map(result, id_map, profiles_map, start_coord=start_coord)
    
    # Build markers
    markers = []
    for p in profiles:
        if p.latitude is None or p.longitude is None:
            continue
        markers.append({
            "lat": p.latitude,
            "lon": p.longitude,
            "color": "#42326E",
            "id": p.id,
            "name": p.name,
            "personality": p.personality,
            "arguments": p.suggested_arguments,
            "nbhood": p.nbhood,
            "preferred_language": p.preferred_language,
            "origin": p.origin,
            "political_scale": p.political_scale,
            "ideal_process": p.ideal_process,
            "strategic_profile": p.strategic_profile,
        })

    # Extract coordinates from GeoJSON
    coordinates = []
    for feature in route_geojson.get("features", []):
        geom = feature.get("geometry", {})
        if geom.get("type") == "LineString":
            coordinates.extend(geom.get("coordinates", []))

    return {
        "start": {"lat": req.start_lat, "lon": req.start_lon},
        "route": {"coordinates": coordinates},
        "markers": markers,
    }

@router.get("/geocode")
async def geocode_address(q: str = Query(..., description="The address to geocode")):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={q}"
    headers = {"User-Agent": "YourAppName/1.0 (contact@example.com)"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        return r.json()
