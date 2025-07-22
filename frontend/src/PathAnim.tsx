import { useEffect } from "react";
import L from "leaflet";
import "leaflet-ant-path";
import { useMap } from "react-leaflet";

export default function PathAnim({ positions, options }) {
  const map = useMap();

  useEffect(() => {
    const antPath = new L.polyline.antPath(positions, options);
    antPath.addTo(map);

    return () => {
      map.removeLayer(antPath);
    };
  }, [map, positions, options]);

  return null;
}