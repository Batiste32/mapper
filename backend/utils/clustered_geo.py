from sklearn.cluster import KMeans
from geopy.distance import geodesic
from math import ceil

from backend.utils.geo import *

def cluster_points(points, max_cluster_size=50):
    """
    Cluster points into spatial batches.
    Returns: list of clusters, each is list of point indexes.
    """
    n_clusters = ceil(len(points) / max_cluster_size)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    coords = [[lon, lat] for lat, lon in points]
    labels = kmeans.fit_predict(coords)

    clusters = [[] for _ in range(n_clusters)]
    for idx, label in enumerate(labels):
        clusters[label].append(idx)

    clusters = enforce_max_cluster_size(clusters, max_cluster_size)
    return clusters

def enforce_max_cluster_size(clusters, max_cluster_size):
    new_clusters = []
    for cluster in clusters:
        if len(cluster) > max_cluster_size:
            for i in range(0, len(cluster), max_cluster_size):
                new_clusters.append(cluster[i:i+max_cluster_size])
        else:
            new_clusters.append(cluster)
    return new_clusters

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
            print(f"WARN Cluster {idx} failed: {e}")
            skipped_points += len(cluster)
            continue

        if result is None or "routes" not in result or not result["routes"]:
            print(f"WARN Cluster {idx} returned no route. Skipping.")
            skipped_points += len(cluster)
            continue

        steps = result["routes"][0].get("steps", [])
        if not steps:
            print(f"WARN Cluster {idx} has no valid steps. Skipping.")
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
            print(f"WARN Cluster {idx} steps all empty. Skipping.")
            skipped_points += len(cluster)
            continue

        full_ordered_points += ordered
        cluster_results.append((ordered, ordered_ids))

    if skipped_points > 0:
        print(f"Warning: {skipped_points} points were skipped due to ORS failures or missing steps.")

    return full_ordered_points, cluster_results

def display_clustered_route(full_ordered_points, cluster_results, start_coord=None):
    """
    Loops through each cluster, retrieves a directions GeoJSON for that cluster,
    and combines them into a single merged GeoJSON FeatureCollection.

    Parameters
    ----------
    full_ordered_points : list of (lat, lon)
        The points in the final visiting order (including all clusters in sequence)
    cluster_results : list
        A list where each element represents a cluster's ordered points
    start_coord : tuple (lat, lon), optional
        Starting coordinate

    Returns
    -------
    dict
        A combined GeoJSON FeatureCollection with all cluster routes merged
    """

    combined_geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    # Track the global order of clusters
    for cluster_idx, cluster_points in enumerate(cluster_results):
        # Prepend start coordinate for the first cluster only
        if cluster_idx == 0 and start_coord:
            points_to_route = [start_coord] + cluster_points
        else:
            points_to_route = cluster_points

        # ORS requires lon, lat order, so get_directions_route will handle that
        if len(points_to_route) < 2:
            print(f"Skipping cluster {cluster_idx} - not enough points.")
            continue

        # Get the route for this cluster
        try:
            cluster_geojson = get_directions_route(points_to_route)

            # Append features to combined FeatureCollection
            if cluster_geojson.get("features"):
                combined_geojson["features"].extend(cluster_geojson["features"])

        except Exception as e:
            print(f"Error getting directions for cluster {cluster_idx}: {e}")
            continue

    return combined_geojson