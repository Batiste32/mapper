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
    Draw final stitched map.
    """
    route_geojson = get_directions_route(full_ordered_points)
    line_coords = route_geojson["features"][0]["geometry"]["coordinates"]
    route_points = [(lat, lon) for lon, lat in line_coords]

    m = folium.Map(location=full_ordered_points[0], zoom_start=13)
    # Add arrows
    AntPath(route_points).add_to(m)
    # Setup gradient
    colors = get_gradient_colors(len(full_ordered_points))

    # START
    folium.Marker(
        location=full_ordered_points[0],
        popup="START",
        icon=folium.Icon(color="green", icon="play", prefix="fa")
    ).add_to(m)

    # Mark all stops with name lookup
    db = SessionLocal()
    for idx, (_, ordered_ids) in enumerate(cluster_results, start=1):
        for stop_idx, profile_id in enumerate(ordered_ids, start=1):
            profile = db.query(Profile).filter(Profile.id == profile_id).first()
            name = profile.name if profile else "Unknown"
            stop_coord = full_ordered_points[stop_idx]
            folium.Marker(
                location=stop_coord,
                popup=f"Stop {stop_idx}: {name}",
                icon=folium.Icon(color=colors[stop_idx],
                             icon="info-sign" if stop_idx > 0 else "play",
                             prefix="glyphicon" if stop_idx > 0 else "fa")
            ).add_to(m)
    db.close()

    folium.PolyLine(route_points, color="red", weight=3).add_to(m)
    m.save("clustered_route_map.html")
    print("Map saved as clustered_route_map.html")