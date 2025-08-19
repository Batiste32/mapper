from math import radians, cos, sin, asin, sqrt
import requests
import csv
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from backend.database.models import Profile
import backend.database as db_module

def haversine(lat1, lon1, lat2, lon2):
    # rayon de la Terre en km
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def geocode_address(address):
    
    url = f"https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()
    if not results:
        return None
    lat = float(results[0]["lat"])
    lon = float(results[0]["lon"])
    return lat, lon

def geocode_address_osm(address: str):
    """
    Use OpenStreetMap Nominatim API to geocode an address.
    Returns (latitude, longitude) as floats, or None if not found.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    response = requests.get(url, params=params, headers={"User-Agent": "ElectoralApp/1.0"})
    response.raise_for_status()
    results = response.json()
    if not results:
        return None
    lat = float(results[0]["lat"])
    lon = float(results[0]["lon"])
    return lat, lon

def update_profiles_latlon_from_csv(engine, filepath="backend/database/profiles.csv"):
    Session = sessionmaker(bind=engine)
    session = Session()
    unresolved_addresses = {}
    total = 0
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            total+=1
            address = row["ADRESS"]
            try :
                latlon = geocode_address_osm(address)
            except Exception as e :
                unresolved_addresses[address] = str(e)
                continue
            if not latlon:
                unresolved_addresses[address] = "Address not found"
                continue

            profile = session.query(Profile).filter(Profile.uniqueid == f"{row['UNIQUEID']}").first()
            if profile:
                profile.latitude, profile.longitude = latlon
                print(f"Updated: {profile.name} => {latlon}")

    session.commit()
    print("Geocoding done & DB updated!")
    return(unresolved_addresses,total)

def compute_straight_dist(start_lat=None, start_lon=None):
    """
    Compute straight-line distance from a starting point to each Profile.
    Updates the `distance` field in meters.
    """
    if start_lat is None or start_lon is None:
        print("Missing start coordinates.")
        return

    db = db_module.SessionLocal()
    print(str(db_module.SessionLocal.kw['bind'].url))
    profiles = db.query(Profile).all()
    updated = 0

    for p in profiles:
        if p.latitude is not None and p.longitude is not None:
            dist_m = haversine(start_lat, start_lon, p.latitude, p.longitude)
            p.distance = dist_m
            updated += 1

    db.commit()
    db.close()
    print(f"Updated distance for {updated} profiles.")

def get_optimized_route(start_lat,start_lon,points,profile_ids,lat_first=True,loop_at_start=False):
    """
    Arranges the points in the best order.
    start = start coordinate
    points = list of coordinates to visit
    profile_ids = list of profile uniqueids associated with the points
    lat_first = coordinates start with latitude ?
    loop_at_start = should the route loop back at starting position ?
    """
    try :
        load_dotenv("/etc/secrets/.env")
    except :
        print("Warning, couldn't load Render env file.\nIgnore if running on local.")

    ORS_API_KEY = os.getenv("ORS_API_KEY")
    if not ORS_API_KEY:
        raise RuntimeError("ORS_API_KEY environment variable is missing.")

    url = "https://api.openrouteservice.org/optimization"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    if lat_first : # ORS needs lon,lat
        coordinates = [[lon, lat] for lat, lon in points]
    else :
        coordinates = points

    if start_lat and start_lon :
        start = [start_lon,start_lat]
    else :
        start = coordinates[0]

    vehicle = {
        "id": 1,
        "start": start,
        "profile": "driving-car"
    }
    if loop_at_start:
        vehicle["end"] = start

    jobs = [] # index, coordinates
    id_map = {} # index, profile uniqueid
    for idx, (real_id, coordinate) in enumerate(zip(profile_ids, coordinates), start=1):
        jobs.append({
            "id": idx,
            "location": coordinate
        })
        id_map[idx] = real_id

    body = {
        "jobs": jobs,
        "vehicles": [vehicle]
    }
    try :
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return (response.json(),id_map)
    except requests.exceptions.HTTPError as e:
        print(f"ORS API returned an HTTPError: {e} | {response.text}")
        return None, None

def get_directions_route(ordered_points):
    """
    Uses real roads/paths to follow.
    ordered_points: list of (lat, lon) tuples in the optimized order.
    """
    try :
        load_dotenv("/etc/secrets/.env")
    except :
        print("Warning, couldn't load Render env file.\nIgnore if running on local.")

    ORS_API_KEY = os.getenv("ORS_API_KEY")
    if not ORS_API_KEY:
        raise RuntimeError("ORS_API_KEY environment variable is missing.")

    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    coordinates=[]

    for lat, lon in ordered_points:
        if (lon > -70) or (lat < 40):
            print(f"WARN coordinates seem outside of expected value :\nlon: {lon}, lat: {lat}")
        coordinates.append([lon, lat]) 

    print(f"Original points : {ordered_points[:10]}...{ordered_points[-10:]}\nRearranged points : {coordinates}")

    body = {
        "coordinates": coordinates,
        "instructions": False
    }

    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()
    return response.json()

def get_gradient_colors(n):
    """
    Return a list of n folium-friendly color names approximating a green -> blue gradient.
    For more precision, use hex codes with custom icons if needed.
    """
    gradient = []
    steps = ["green", "lightgreen", "cadetblue", "blue", "darkblue"]

    if n <= len(steps):
        return steps[:n]

    for i in range(n):
        idx = int(i / n * (len(steps) - 1))
        gradient.append(steps[idx])
    return gradient

def display_route_on_map(result, id_map, profiles, start_coord=None):
    """
    Calls get_directions_route.
    result: JSON returned by get_optimized_route()
    id_map: {job_id: profile_uniqueid}
    profiles: dict of {profile_uniqueid: (lat, lon)}
    start_coord: tuple (lat, lon) of starting point
    """

    if result is None or id_map is None:
        print("No route result to display. Check your ORS request.")
        return

    # Extract ordered job IDs
    steps = result["routes"][0]["steps"]
    ordered_points = []
    ordered_ids = []  # Store profile IDs
    for step in steps:
        if step["type"] == "job":
            job_id = step["job"]
            profile_id = id_map[job_id]
            ordered_points.append(profiles[profile_id])  # (lat, lon)
            ordered_ids.append(profile_id)

    if not ordered_points:
        print("No route steps found.")
        return

    if start_coord:
        ordered_points = [start_coord] + ordered_points

    # Get real route
    route_geojson = get_directions_route(ordered_points)
    line_coords = route_geojson["features"][0]["geometry"]["coordinates"]  # [ [lon, lat], ... ]

    # Load names
    db = db_module.SessionLocal()
    print(str(db_module.SessionLocal.kw['bind'].url))
    profile_names = {}
    profile_arguments = {}
    profile_age = {}
    profile_nbhood = {}
    profile_preferred_language = {}
    profile_origin = {}
    profile_political_scale = {}
    profile_ideal_process = {}
    profile_strategic_profile = {}
    profile_personality = {}
    profiles_db = db.query(Profile).filter(Profile.id.in_(ordered_ids)).all()
    for p in profiles_db:
        profile_names[p.id] = p.name
        profile_arguments[p.id] = p.suggested_arguments
        profile_age[p.id] = p.age
        profile_nbhood[p.id] = p.nbhood
        profile_preferred_language[p.id] = p.preferred_language
        profile_origin[p.id] = p.origin
        profile_political_scale[p.id] = p.political_scale
        profile_ideal_process[p.id] = p.ideal_process
        profile_strategic_profile[p.id] = p.strategic_profile
        profile_personality[p.id] = p.personality
    db.close()

    markers = []
    for (lat, lon), profile_id in zip(ordered_points[1:], ordered_ids):
        markers.append({
            "id": profile_id,
            "name": profile_names.get(profile_id, "Unknown"),
            "arguments": profile_arguments.get(profile_id, "None"),
            "age": profile_age.get(profile_id, "None"),
            "nbhood": profile_nbhood.get(profile_id, "None"),
            "preferred_language": profile_preferred_language.get(profile_id, "None"),
            "origin": profile_origin.get(profile_id, "None"),
            "political_scale": profile_political_scale.get(profile_id, "None"),
            "ideal_process": profile_ideal_process.get(profile_id, "None"),
            "strategic_profile": profile_strategic_profile.get(profile_id, "None"),
            "personality": profile_personality.get(profile_id, "None"),
            "lat": lat,
            "lon": lon
        })

    return {
        "start": {
            "lat": start_coord[0],
            "lon": start_coord[1]
        },
        "markers": markers,
        "route": {
            "type": "LineString",
            "coordinates": line_coords  # Still [ [lon, lat], ... ]
        }
    }

def test_map():
    # Example data:
    start_lat = 45.47
    start_lon = -73.62
    points = [(45.48, -73.63), (45.49, -73.64)]
    profile_ids = [101, 102]

    # Call your optimizer:
    result, id_map = get_optimized_route(start_lat, start_lon, points, profile_ids)

    # Make a dict of profiles: {profile_id: (lat, lon)}
    profiles = {
        101: (45.48, -73.63),
        102: (45.49, -73.64)
    }

    # Draw map:
    display_route_on_map(result, id_map, profiles, (start_lat,start_lon))