from sklearn.cluster import KMeans
import requests
import folium
from geopy.distance import geodesic
from backend.database import SessionLocal
from backend.database.models import Profile
from backend.utils.geo import *

def cluster_points(points, max_cluster_size=70):
    """
    Cluster points into spatial batches.
    Returns: list of clusters, each is list of point indexes.
    """
    n_clusters = max(1, len(points) // max_cluster_size + 1)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    coords = [[lon, lat] for lat, lon in points]
    labels = kmeans.fit_predict(coords)

    clusters = [[] for _ in range(n_clusters)]
    for idx, label in enumerate(labels):
        clusters[label].append(idx)

    return clusters

def combine_cluster_routes(start_coord, clusters, points, profile_ids):
    """
    1. Runs optimization per cluster.
    2. Order clusters by centroid distance from start.
    3. Glue all segments in logical order.
    """
    cluster_results = []
    skipped_points = 0

    # Build cluster centroids
    centroids = []
    for cluster in clusters:
        lat = sum(points[i][0] for i in cluster) / len(cluster)
        lon = sum(points[i][1] for i in cluster) / len(cluster)
        centroids.append((lat, lon))

    # Sort clusters by distance from start
    cluster_order = sorted(
        range(len(clusters)),
        key=lambda i: geodesic(start_coord, centroids[i]).meters
    )

    full_ordered_points = [start_coord]

    for idx in cluster_order:
        cluster = clusters[idx]
        cluster_points = [points[i] for i in cluster]
        cluster_ids = [profile_ids[i] for i in cluster]

        try:
            result, id_map = get_optimized_route(start_coord[0],start_coord[1],points=cluster_points,profile_ids=cluster_ids)
        except Exception as e:
            print(f"❗ Cluster {idx} failed: {e}")
            skipped_points += len(cluster)
            continue

        if result is None or "routes" not in result or not result["routes"]:
            print(f"❗ Cluster {idx} returned no route. Skipping.")
            skipped_points += len(cluster)
            continue

        steps = result["routes"][0].get("steps", [])
        if not steps:
            print(f"❗ Cluster {idx} has no valid steps. Skipping.")
            skipped_points += len(cluster)
            continue

        ordered = []
        ordered_ids = []

        for step in steps:
            if step["type"] == "job":
                job_id = step["job"]
                profile_id = id_map.get(job_id)
                if profile_id is None:
                    continue
                ordered.append(cluster_points[job_id - 1])
                ordered_ids.append(profile_id)

        if not ordered:
            print(f"❗ Cluster {idx} steps all empty. Skipping.")
            skipped_points += len(cluster)
            continue

        full_ordered_points += ordered
        cluster_results.append((ordered, ordered_ids))

    if skipped_points > 0:
        print(f"Warning: {skipped_points} points were skipped due to ORS failures or missing steps.")

    return full_ordered_points, cluster_results

def display_clustered_route(full_ordered_points, cluster_results, start_coord=None):
    """
    Returns a structured JSON for the final stitched map with all clusters.
    
    Parameters:
    - full_ordered_points: [(lat, lon), ...] the complete ordered route including start
    - cluster_results: list of (cluster_center, [profile_id, ...])
    - start_coord: optional (lat, lon) tuple
    
    Returns:
    {
        "start": { "lat": ..., "lon": ... },
        "markers": [ { "id": ..., "name": ..., "lat": ..., "lon": ..., "color": ... }, ... ],
        "route": {
            "type": "LineString",
            "coordinates": [[lon, lat], ...]
        }
    }
    """
    if not full_ordered_points or not cluster_results:
        print("Missing data for clustered route display.")
        return

    # Get directions
    route_geojson = get_directions_route(full_ordered_points)
    line_coords = route_geojson["features"][0]["geometry"]["coordinates"]  # [[lon, lat], ...]

    # Optional color gradient
    colors = get_gradient_colors(len(full_ordered_points))

    # Load all involved profile names
    profile_ids = [pid for _, cluster in cluster_results for pid in cluster]
    db = SessionLocal()
    profile_map = {p.id: p.name for p in db.query(Profile).filter(Profile.id.in_(profile_ids)).all()}
    profile_arguments = {p.id : p.suggested_arguments for p in db.query(Profile).filter(Profile.id.in_(profile_ids)).all()}
    profile_age = {p.id : p.age for p in db.query(Profile).filter(Profile.id.in_(profile_ids)).all()}
    profile_nbhood = {p.id : p.nbhood for p in db.query(Profile).filter(Profile.id.in_(profile_ids)).all()}
    profile_preferred_language = {p.id : p.preferred_language for p in db.query(Profile).filter(Profile.id.in_(profile_ids)).all()}
    profile_origin = {p.id : p.origin for p in db.query(Profile).filter(Profile.id.in_(profile_ids)).all()}
    profile_political_scale = {p.id : p.political_scale for p in db.query(Profile).filter(Profile.id.in_(profile_ids)).all()}
    profile_ideal_process = {p.id : p.ideal_process for p in db.query(Profile).filter(Profile.id.in_(profile_ids)).all()}
    profile_strategic_profile = {p.id : p.strategic_profile for p in db.query(Profile).filter(Profile.id.in_(profile_ids)).all()}
    db.close()

    # Build marker list
    markers = []
    point_idx = 1  # Start at 1 since index 0 is the start_coord

    for (_, ordered_ids) in cluster_results:
        for profile_id in ordered_ids:
            if point_idx >= len(full_ordered_points):
                print(f"Warning: Index {point_idx} out of range for coordinates.")
                continue
            lat, lon = full_ordered_points[point_idx]
            markers.append({
                "id": profile_id,
                "name": profile_map.get(profile_id, "Unknown"),
                "arguments": profile_arguments.get(profile_id, "None"),
                "age": profile_age.get(profile_id, "None"),
                "nbhood": profile_nbhood.get(profile_id, "None"),
                "preferred_language": profile_preferred_language.get(profile_id, "None"),
                "origin": profile_origin.get(profile_id, "None"),
                "political_scale": profile_political_scale.get(profile_id, "None"),
                "ideal_process": profile_ideal_process.get(profile_id, "None"),
                "strategic_profile": profile_strategic_profile.get(profile_id, "None"),
                "lat": lat,
                "lon": lon,
                "color": colors[point_idx]  # Optional gradient color
            })
            point_idx += 1

    if not start_coord:
        start_coord = full_ordered_points[0]

    return {
        "start": {
            "lat": start_coord[0],
            "lon": start_coord[1]
        },
        "markers": markers,
        "route": {
            "type": "LineString",
            "coordinates": line_coords  # [[lon, lat], ...]
        }
    }