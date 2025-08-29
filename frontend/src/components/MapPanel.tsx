import { MapContainer, TileLayer, Marker, Tooltip } from "react-leaflet";
import L from "leaflet";
import type { LatLngExpression } from "leaflet";
import PathAnim from "./PathAnim";

interface MarkerProperties {
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
}

interface MarkerData {
  position: LatLngExpression;
  color: string;
  properties: MarkerProperties;
}

interface MapPanelProps {
  start: LatLngExpression;
  route: LatLngExpression[] | null;
  markers: MarkerData[];
  selectedProfile: MarkerProperties | null;
  ToggleProfileDisplay: (props: MarkerProperties) => void;
}

export default function MapPanel({
  start,
  route,
  markers,
  selectedProfile,
  ToggleProfileDisplay,
}: MapPanelProps) {
  const defaultIcon = L.icon({
    iconUrl:
      "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
    shadowUrl:
      "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
  });

  const selectedIcon = L.icon({
    iconUrl:
      "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-violet.png",
    shadowUrl:
      "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
    iconSize: [30, 46],
    iconAnchor: [12, 41],
  });

  const startIcon = L.icon({
    iconUrl:
      "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
    shadowUrl:
      "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
  });

  return (
    <div
      className={`flex-1 h-[50vh] sm:h-full z-0 relative`}
    >
      <MapContainer center={start} zoom={13} className="flex-1 h-full absolute inset-0 z-0">
        <TileLayer
          url="https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://osm.org/copyright">OSM</a>'
        />
        <Marker
          position={start}
          icon={startIcon}
          eventHandlers={{
            mouseover: (e) => {
              e.target.openTooltip();
            },
            mouseout: (e) => {
              e.target.closeTooltip();
            },
          }}
        >
          <Tooltip direction="top" offset={[0, -10]} opacity={1} className="fade-tooltip">
            Start Position
          </Tooltip>
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
            icon={selectedProfile?.index === m.properties.index ? selectedIcon : defaultIcon}
            eventHandlers={{
              mouseover: (e) => e.target.openTooltip(),
              mouseout: (e) => e.target.closeTooltip(),
              click: () => ToggleProfileDisplay(m.properties),
            }}
          >
            <Tooltip direction="top" offset={[0, -10]} opacity={1} className="fade-tooltip">
              <div>
                <strong>
                  #{m.properties.index} – {m.properties.name}
                </strong>
              </div>
            </Tooltip>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
