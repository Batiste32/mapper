import { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Polyline, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

import PathAnim from "./PathAnim.tsx"

// Fix Leaflet's default icon path
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

export default function App() {
  const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`;
  const [start, setStart] = useState([45.45, -73.64]);
  const [filters, setFilters] = useState({
    ethnicity: "",
    political_alignment: "",
    min_score_vote: "",
  });
  const [route, setRoute] = useState(null);
  const [markers, setMarkers] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [startAddress, setStartAddress] = useState("");

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
        console.error("Geocoding error:", error);
        alert("Geocoding failed. Falling back to geolocation.");
        alert(error);
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
        name: m.name,
        arguments: m.arguments,
        id: m.id,
      },
    }));

    setMarkers(markerList);
  };

  return (
    <div className="flex flex-col sm:flex-row h-screen w-screen bg-midnight">
      
      {/* FILTER PANEL (Top on mobile, left on desktop) */}
      <div className="w-full sm:w-64 p-4 bg-midnight border-b sm:border-b-0 sm:border-r max-h-[30vh] sm:max-h-none overflow-auto z-10">
        <h2 className="text-xl font-semibold mb-4">Filters</h2>
        <label className="block mb-2">
          Ethnicity:
          <input
            className="w-full border rounded p-1"
            value={filters.ethnicity}
            onChange={(e) => setFilters({ ...filters, ethnicity: e.target.value })}
          />
        </label>
        <label className="block mb-2">
          Political Alignment:
          <input
            className="w-full border rounded p-1"
            value={filters.political_alignment}
            onChange={(e) => setFilters({ ...filters, political_alignment: e.target.value })}
          />
        </label>
        <label className="block mb-2">
          Min Vote Score:
          <input
            type="number"
            className="w-full border rounded p-1"
            value={filters.min_score_vote}
            onChange={(e) => setFilters({ ...filters, min_score_vote: parseFloat(e.target.value) })}
          />
        </label>
        <input
          type="text"
          value={startAddress}
          onChange={(e) => setStartAddress(e.target.value)}
          placeholder="Start address (leave blank to use GPS)"
          className="border p-2 rounded w-full"
        />
        <button
          onClick={handleSearch}
          className="mt-4 w-full bg-purple hover:bg-lavender text-white p-2 rounded"
        >
          Search
        </button>
      </div>

      {/* MAP PANEL */}
      {/* <div className="flex-1 h-[50vh] sm:h-full z-0"> */}
      <div className={`transition-width flex-1 ${selectedProfile ? "sm:w-1/4" : ""} h-[50vh] sm:h-full z-0 relative`}>
        <MapContainer center={start} zoom={13} className="flex-1 h-full absolute inset-0 z-0">
          <TileLayer
            url="https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://osm.org/copyright">OSM</a>'
          />
          <Marker position={start}>
            <Popup>Start Position</Popup>
          </Marker>
          {route && (
            <PathAnim
              positions={route}
              options={{
                delay: 800,
                dashArray: [10, 20],
                weight: 5,
                color: "#0078ff",
                pulseColor: "#00f0ff",
                paused: false,
                reverse: false,
                hardwareAccelerated: true,
              }}
            />
          )}
          {markers.map((m, idx) => (
            <Marker
              key={idx}
              position={m.position}
              eventHandlers={{
                click: () => setSelectedProfile(m.properties),
              }}
            >
              <Popup>
                <div>
                  <strong>#{m.properties.index} – {m.properties.name}</strong>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* PROFILE PANEL (Bottom on mobile, right on desktop) */}
      {/* <div className="w-full sm:w-64 p-4 bg-midnight border-t sm:border-t-0 sm:border-l max-h-[30vh] sm:max-h-none overflow-auto z-10"> */}
      <div className={`w-full p-4 bg-midnight border-t sm:border-t-0 sm:border-l max-h-[30vh] sm:max-h-none overflow-auto z-10
        transition-all duration-300 ease-in-out
        ${selectedProfile ? "sm:w-1/2" : "sm:w-64"} `} >
        <h2 className="text-xl font-semibold mb-4">Profile Info</h2>
        {selectedProfile ? (
          <div>
            {Object.entries(selectedProfile).map(([k, v]) => (
              <p key={k}><strong>{k}</strong>: {v}</p>
            ))}
          </div>
        ) : (
          <p>No profile selected.</p>
        )}
      </div>
    </div>
  );
}
