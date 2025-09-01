import { useState, useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

import CollapsePanel from "./components/CollapsePanel";
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
    picture_url: string;
  };
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

  const resetAll = () => {
    setRoute(null);
    setMarkers([]);
    setSelectedProfile(null);
    setStart([45.45, -73.64]); // reset to default center

    // Notify FilterPanel to reset itself
    const resetEvent = new CustomEvent("reset-filters");
    window.dispatchEvent(resetEvent);
  };


  const applyFilters = async (raw: Record<string, any>) => {
    setMapperWait(true);
    try {
      // default to current map start
      let lat = start[0];
      let lon = start[1];

      // allow either start_lat/lon from panel or a startAddress to geocode
      if (raw.start_lat && raw.start_lon) {
        lat = parseFloat(String(raw.start_lat));
        lon = parseFloat(String(raw.start_lon));
      } else if (raw.startAddress && String(raw.startAddress).trim()) {
        const geoRes = await fetch(`${API_BASE}/geocode?q=${encodeURIComponent(raw.startAddress)}`,
          { headers: { "ngrok-skip-browser-warning": "true" } });
        const geoData = await geoRes.json();
        if (Array.isArray(geoData) && geoData.length) {
          lat = parseFloat(geoData[0].lat);
          lon = parseFloat(geoData[0].lon);
        }
      }
      console.log("Starting from :",lat,lon);
      // drop any start_* keys and build the nested filters object
      const { start_lat: _slat, start_lon: _slon, startAddress: _saddr, ...rest } = raw;

      // map friendly -> DB field names (optional; backend also supports this)
      const aliasMap: Record<string, string> = {
        ethnicity: "origin",
        political_alignment: "political_lean",
        min_score_vote: "score_vote",
      };

      const cleaned: Record<string, any> = {};
      for (const [k, v] of Object.entries(rest)) {
        if (v === "" || v === null || v === undefined) continue;
        const key = aliasMap[k] ?? k;
        if (k === "min_score_vote") {
          cleaned[key] = { gte: Number(v) };
        } else {
          cleaned[key] = v;
        }
      }

      const payload = { start_lat: lat, start_lon: lon, filters: cleaned };
      console.log("Sending payload :",payload);
      const res = await fetch(`${API_BASE}/profiles/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "ngrok-skip-browser-warning": "true" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!data || !data.route || !data.start) {
        console.warn("No route returned:", data);
        if (data?.message) alert(data.message);
        setRoute(null);
        setMarkers([]);
        return;
      }

      setStart([data.start.lat, data.start.lon]);
      const routeLatLng = data.route.coordinates.map(([lon2, lat2]: [number, number]) => [lat2, lon2]);
      setRoute(routeLatLng);

      const markerList = data.markers.map((m: any, idx: number) => ({
        position: [m.lat, m.lon] as [number, number],
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
          picture_url: m.picture_url,
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
        {/* Left collapsible panel (Filters) */}
        <CollapsePanel direction="left" className="w-1/3">
          <FilterPanel applyFilters={applyFilters} mapperWait={mapperWait} />
        </CollapsePanel>

        {/* Center map always expands */}
        <div className="flex-1">
          <MapPanel
            start={start}
            route={route}
            markers={markers}
            selectedProfile={selectedProfile}
            ToggleProfileDisplay={ToggleProfileDisplay}
          />
        </div>

        {/* Right collapsible panel (Profile) */}
        <CollapsePanel direction="right" className="w-1/3">
          <ProfilePanel selectedProfile={selectedProfile} />
        </CollapsePanel>
      </div>
      <div className="flex flex-row">
        <button
          onClick={goBack}
          className="flex-1 p-4 m-4 bg-purple hover:bg-lavender text-white rounded"
        >
          Back to Upload
        </button>
        <button
          onClick={resetAll}
          className="flex-1 p-4 m-4 bg-purple hover:bg-lavender text-white rounded"
        >
          Reset Map
        </button>
      </div>
    </div>
  );
}