import { useEffect } from "react";
import L from "leaflet";
import type { LatLngExpression, PolylineOptions } from "leaflet";
import "leaflet-ant-path";
import { useMap } from "react-leaflet";

interface PathAnimProps {
  positions: LatLngExpression[]; // list of coordinates
  options?: PolylineOptions & {
    delay?: number;
    dashArray?: [number, number];
    weight?: number;
    color?: string;
    pulseColor?: string;
    paused?: boolean;
    reverse?: boolean;
    hardwareAccelerated?: boolean;
  };
}

export default function PathAnim({ positions, options }: PathAnimProps) {
  const map = useMap();

  useEffect(() => {
    // `antPath` is not defined in Leaflet's official typings, so we cast
    const antPath = (L as any).polyline.antPath(positions, options);
    antPath.addTo(map);

    return () => {
      map.removeLayer(antPath);
    };
  }, [map, positions, options]);

  return null;
}
