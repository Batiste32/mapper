import { useState, useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

import FilterPanel from "./components/FilterPanel.tsx";
import MapPanel from "./components/MapPanel.tsx";
import ProfilePanel from "./components/ProfilePanel.tsx";

import './App.css'

// Fix Leaflet's default icon path
delete L.Icon.Default.prototype._getIconUrl;
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

export default function App() {
  const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`;
  const [start, setStart] = useState([45.45, -73.64]);
  const [filters, setFilters] = useState({
    ethnicity: "",
    political_alignment: "",
    min_score_vote: "",
  });
  const [route, setRoute] = useState<LatLng[] | null>(null);
  const [markers, setMarkers] = useState<Marker[]>([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [startAddress, setStartAddress] = useState("");

  /* Valid database input fields */
  const [validEthnicities, setValidEthnicities] = useState([]);
  const [validAlignments, setValidAlignments] = useState([]);

  useEffect(() => {
    if (!startAddress) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setStart([pos.coords.latitude, pos.coords.longitude]);
        },
        () => {}
      );
    }
  }, [startAddress]);

  useEffect(() => {
    let watchId;

    if (startAddress.trim() === "") {
      if (navigator.geolocation) {
        watchId = navigator.geolocation.watchPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            const newPos = [latitude, longitude];

            setStart(newPos);

            setRoute((prevRoute) => {
              if (!prevRoute) return null;
              return trimRoute(newPos, prevRoute);
            });
          },
          (err) => {
            console.error("Geolocation error:", err);
          },
          { enableHighAccuracy: true, maximumAge: 10000, timeout: 5000 }
        );
      }
    }

    return () => {
      if (watchId) navigator.geolocation.clearWatch(watchId);
    };
  }, [startAddress]);

  const fetchValidValues = async (field: string, setter: React.Dispatch<React.SetStateAction<never[]>>) => {
    try {
      const res = await fetch(`http://localhost:8000/profiles/valid_values?field=${field}`);
      const data = await res.json();
      setter(data);
    } catch (err) {
      console.error(`Failed to fetch values for field "${field}":`, err);
      setter([]);
    }
  };

  useEffect(() => {
    fetchValidValues("origin", setValidEthnicities);
    fetchValidValues("political_lean", setValidAlignments);
  }, []);

  const handleSearch = async () => {
    let lat = start[0];
    let lon = start[1];

    // If user entered an address, geocode it via your FastAPI backend
    if (startAddress.trim()) {
      try {
        const geoRes = await fetch(
          `${API_BASE}/geocode?q=${encodeURIComponent(startAddress)}`
        );
        const geoData = await geoRes.json();

        if (geoData.length > 0) {
          lat = parseFloat(geoData[0].lat);
          lon = parseFloat(geoData[0].lon);
        } else {
          alert("Address not found. Falling back to geolocation.");
        }
      } catch (error) {
        alert("Geocoding failed. Falling back to geolocation.");
        console.error("Geocoding error:", error);
      }
    }
    alert(`${API_BASE}/profiles/optimize`);
    const res = await fetch(`${API_BASE}/profiles/optimize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...filters,
        start_lat: lat,
        start_lon: lon,
      }),
    });

    const data = await res.json();
    console.log(data);

    setStart([data.start.lat, data.start.lon]);

    const routeLatLng = data.route.coordinates.map(([lon, lat]) => [lat, lon]);
    setRoute(routeLatLng);

    const markerList = data.markers.map((m, idx) => ({
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
  };

  const ToggleProfileDisplay = (properties) => {
    setSelectedProfile((prev) => prev && prev.array_id === properties.array_id ? null : properties)
  }

  function trimRoute(currentPosition, route) {
    const threshold = 0.0005; // approx 50m depending on lat/lon
    return route.filter(([lat, lon]) => {
      const dist = Math.sqrt(
        Math.pow(currentPosition[0] - lat, 2) + Math.pow(currentPosition[1] - lon, 2)
      );
      return dist > threshold;
    });
  }

  return (
    <div className="flex flex-col sm:flex-row h-screen w-screen bg-midnight">
      
      <FilterPanel filters={filters} setFilters={setFilters}
        startAddress={startAddress} setStartAddress={setStartAddress} handleSearch={handleSearch} 
        validEthnicities={validEthnicities} validAlignments={validAlignments}/>

      <MapPanel start={start} route={route} markers={markers} selectedProfile={selectedProfile} ToggleProfileDisplay={ToggleProfileDisplay} />

      <ProfilePanel selectedProfile={selectedProfile} />
    </div>
  );
}
