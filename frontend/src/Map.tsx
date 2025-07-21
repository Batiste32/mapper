import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';

interface MapProps {
  startCoordinate: LatLngExpression; // e.g. [48.8566, 2.3522]
}

export default function Map({ startCoordinate }: MapProps) {
  return (
    <div className='h-screen w-screen'>
      <MapContainer
        center={startCoordinate}
        zoom={13}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://osm.org/copyright">OSM</a>'
        />
        <Marker position={startCoordinate}>
          <Popup>Start Position</Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}