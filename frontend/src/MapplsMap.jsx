import React, { useEffect, useRef, useState } from 'react';

const MapplsMap = ({ center, diversionRoute, radius }) => {
  const mapInstance = useRef(null);
  const polylineInstance = useRef(null);
  const markerInstance = useRef(null);
  const circleInstance = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize Map once
  useEffect(() => {
    if (!window.mappls || mapInstance.current) {
      return;
    }

    try {
      mapInstance.current = new window.mappls.Map("mappls-map-container", {
        center: [center.lat, center.lng],
        zoom: 15,
      });

      mapInstance.current.addListener('load', () => {
        setMapLoaded(true);
      });
    } catch (e) {
      console.error("Map Init Error:", e);
    }
  }, []); // Run only once on mount

  // Update center and draw markers/polylines when props change or map loads
  useEffect(() => {
    if (!mapLoaded || !mapInstance.current) return;

    try {
      if (typeof mapInstance.current.setCenter === 'function') {
        mapInstance.current.setCenter([center.lat, center.lng]);
      }

      // Add Marker
      if (markerInstance.current) {
        markerInstance.current.remove();
      }
      markerInstance.current = new window.mappls.Marker({
        map: mapInstance.current,
        position: { lat: center.lat, lng: center.lng },
        popupHtml: "<div style='padding:5px;font-weight:bold;'>Incident Location</div>",
        popupOptions: { openPopup: true }
      });

      // Add Polyline
      if (polylineInstance.current) {
        if (typeof polylineInstance.current.remove === 'function') {
          polylineInstance.current.remove();
        }
      }
      
      if (diversionRoute && diversionRoute.length > 0) {
        const path = diversionRoute.map(coord => ({ lat: coord.lat, lng: coord.lng }));
        
        polylineInstance.current = new window.mappls.Polyline({
          map: mapInstance.current,
          path: path,
          strokeColor: "#047BD5", // fk-blue
          strokeOpacity: 1.0,
          strokeWeight: 6,
          fitbounds: true
        });
      }

      // Add Heatmap Circle
      if (circleInstance.current) {
        if (typeof circleInstance.current.remove === 'function') {
          circleInstance.current.remove();
        }
      }

      if (radius) {
        circleInstance.current = new window.mappls.Circle({
          map: mapInstance.current,
          center: { lat: center.lat, lng: center.lng },
          radius: radius,
          fillColor: "#ff0000",
          fillOpacity: 0.1,
          strokeColor: "transparent",
          strokeWeight: 0,
        });
      }

    } catch (e) {
      console.error("Map Update Error:", e);
    }
  }, [center, diversionRoute, radius, mapLoaded]);

  return <div id="mappls-map-container" style={{ width: '100%', height: '100%', minHeight: '300px', borderRadius: '12px' }}></div>;
};

export default MapplsMap;
