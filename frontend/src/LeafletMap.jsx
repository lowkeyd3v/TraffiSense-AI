import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, useMap } from 'react-leaflet';

// react-leaflet's <MapContainer center=...> only sets the INITIAL view.
// This helper re-centers the map whenever `center` changes after mount —
// mirrors the old mapInstance.current.setCenter(...) call.
function RecenterOnChange({ center }) {
  const map = useMap();
  React.useEffect(() => {
    map.setView([center.lat, center.lng]);
  }, [center.lat, center.lng]); // eslint-disable-line react-hooks/exhaustive-deps
  return null;
}

const LeafletMap = ({ center, diversionRoute, radius }) => {
  const path = diversionRoute && diversionRoute.length > 0
    ? diversionRoute.map(coord => [coord.lat, coord.lng])
    : null;

  return (
    <MapContainer
      center={[center.lat, center.lng]}
      zoom={15}
      style={{ width: '100%', height: '400px', borderRadius: '12px' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />

      <RecenterOnChange center={center} />

      <Marker position={[center.lat, center.lng]}>
        <Popup>Incident Location</Popup>
      </Marker>

      {path && (
        <Polyline
          positions={path}
          pathOptions={{ color: '#047BD5', opacity: 1.0, weight: 6 }}
        />
      )}

      {radius && (
        <Circle
          center={[center.lat, center.lng]}
          radius={radius}
          pathOptions={{ fillColor: '#ff0000', fillOpacity: 0.1, color: 'transparent', weight: 0 }}
        />
      )}
    </MapContainer>
  );
};

export default LeafletMap;
