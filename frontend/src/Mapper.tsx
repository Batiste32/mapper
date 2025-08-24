import { useState, useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

import FilterPanel from "./components/FilterPanel";
import MapPanel from "./components/MapPanel";
import ProfilePanel from "./components/ProfilePanel";

import "./App.css";

(L.Icon.Default.prototype as any)._getIconUrl = undefined;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

type LatLng = [number, number];

type Marker = {
  position: LatLng;
  color: string;
  properties: {
    index: number;
    array_id: string;
    name: string;
    personality: string;
    arguments: string;
    nbhood: string;
    preferred_language: string;
    origin: string;
    political_scale: string;
    ideal_process: string;
    strategic_profile: string;
  };
};

type MarkerData = {
  lat: number;
  lon: number;
  color: string;
  id: string;
  name: string;
  personality: string;
  arguments: string;
  nbhood: string;
  preferred_language: string;
  origin: string;
  political_scale: string;
  ideal_process: string;
  strategic_profile: string;
};

type Props = {
  goBack: () => void;
};

export default function Mapper({ goBack }: Props) {
  const API_BASE = import.meta.env.VITE_API_BASE;
  const [start, setStart] = useState<LatLng>([45.45, -73.64]);
  const [route, setRoute] = useState<LatLng[] | null>(null);
  const [markers, setMarkers] = useState<Marker[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<Marker["properties"] | null>(null);
  const [mapperWait, setMapperWait] = useState<boolean>(false);

  const applyFilters = async (filters: Record<string, any>) => {
    setMapperWait(true);

    let lat: number = start[0];
    let lon: number = start[1];

    if (filters.startAddress && filters.startAddress.trim()) {
      try {
        const geoRes = await fetch(
          `${API_BASE}/geocode?q=${encodeURIComponent(filters.startAddress)}`,
          { headers: { "ngrok-skip-browser-warning": "true" } }
        );
        const geoData = await geoRes.json();
        if (geoData.length > 0) {
          lat = parseFloat(geoData[0].lat);
          lon = parseFloat(geoData[0].lon);
        }
      } catch (error) {
        console.error("Geocoding error:", error);
      }
    }

    const safeFilters = {
      ...filters,
      ...(filters.min_score_vote === "" && { min_score_vote: undefined }),
      start_lat: lat,
      start_lon: lon,
    };

    try {
      const res = await fetch(`${API_BASE}/profiles/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "ngrok-skip-browser-warning": "true" },
        body: JSON.stringify(safeFilters),
      });
      const data = await res.json();

      setStart([data.start.lat, data.start.lon]);
      const routeLatLng = data.route.coordinates.map(
        ([lon, lat]: [number, number]) => [lat, lon]
      );
      setRoute(routeLatLng);

      const markerList = data.markers.map((m: MarkerData, idx: number) => ({
        position: [m.lat, m.lon],
        color: m.color,
        properties: {
          index: idx + 1,
          array_id: m.id,
          name: m.name,
          personality: m.personality,
          arguments: m.arguments,
          nbhood: m.nbhood,
          preferred_language: m.preferred_language,
          origin: m.origin,
          political_scale: m.political_scale,
          ideal_process: m.ideal_process,
          strategic_profile: m.strategic_profile,
        },
      }));

      setMarkers(markerList);
    } catch (err) {
      console.error("Failed to search:", err);
    } finally {
      setMapperWait(false);
    }
  };

  const ToggleProfileDisplay = (properties: Marker["properties"]) => {
    setSelectedProfile((prev) =>
      prev && prev.array_id === properties.array_id ? null : properties
    );
  };

  return (
    <div className="flex flex-col h-full bg-midnight" id="mapper-main">
      <div
        className="flex-1 flex flex-col sm:flex-row bg-midnight h-screen"
        id="panels-layout"
      >
        <FilterPanel applyFilters={applyFilters} />

        <MapPanel
          start={start}
          route={route}
          markers={markers}
          selectedProfile={selectedProfile}
          ToggleProfileDisplay={ToggleProfileDisplay}
        />

        <ProfilePanel selectedProfile={selectedProfile} />
      </div>
      <button
        onClick={goBack}
        className="p-4 m-4 bg-purple hover:bg-lavender text-white rounded"
      >
        Back to Upload
      </button>
    </div>
  );
}