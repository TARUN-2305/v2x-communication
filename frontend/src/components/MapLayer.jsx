import { MapContainer, Marker, Polyline, TileLayer, Tooltip, CircleMarker } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const busIcon = (label, color = '#f97316', action = 'PROCEED') => {
  const bg = action === 'HOLD'
    ? 'linear-gradient(135deg,#eab308,#ca8a04)'
    : action === 'SKIP_STOP'
      ? 'linear-gradient(135deg,#f97316,#ea580c)'
      : `linear-gradient(135deg,${color},${color}cc)`
  return L.divIcon({
    className: '',
    html: `<div style="background:${bg};color:#fff;border:2px solid rgba(255,255,255,.6);
           padding:5px 8px;border-radius:999px;font:700 11px/1 ui-sans-serif;
           box-shadow:0 6px 16px rgba(0,0,0,.4);white-space:nowrap;">${label}</div>`,
    iconSize: [72, 26],
    iconAnchor: [36, 13],
  })
}

function stopColor(waiting) {
  if (waiting >= 30) return '#ef4444'
  if (waiting >= 15) return '#f97316'
  if (waiting >= 6)  return '#facc15'
  return '#34d399'
}

export default function MapLayer({ routePolyline, buses, stops }) {
  const center = routePolyline?.[Math.floor(routePolyline.length / 2)] ?? [12.8858, 77.5738]

  return (
    <MapContainer center={center} zoom={12} scrollWheelZoom className="h-[520px] w-full">
      <TileLayer
        attribution='&copy; <a href="https://carto.com">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        maxZoom={19}
      />

      {/* Route 378 polyline — real OSRM road geometry */}
      <Polyline
        positions={routePolyline}
        pathOptions={{ color: '#22d3ee', weight: 4, opacity: 0.7 }}
      />

      {/* Stop crowd-pressure circles */}
      {stops.map(stop => (
        <CircleMarker
          key={stop.name}
          center={[stop.lat, stop.lng]}
          radius={Math.max(6, Math.min(22, 6 + stop.waiting * 0.5))}
          pathOptions={{
            color: stopColor(stop.waiting),
            fillColor: stopColor(stop.waiting),
            fillOpacity: 0.35, weight: 1.5,
          }}
        >
          <Tooltip direction="top" offset={[0, -8]} opacity={1}>
            <div className="text-xs">
              <strong>{stop.name}</strong>
              <div>{stop.waiting} waiting</div>
            </div>
          </Tooltip>
        </CircleMarker>
      ))}

      {/* Bus markers — colored by bus, outlined by action */}
      {buses?.map(bus => (
        <Marker
          key={bus.id}
          position={[bus.lat, bus.lng]}
          icon={busIcon(bus.id.replace('_', ' '), bus.color, bus.action)}
        >
          <Tooltip direction="top" offset={[0, -10]} opacity={1}>
            <div className="text-xs space-y-0.5">
              <strong>{bus.id}</strong>
              <div>{bus.passengers} pax · {bus.action}</div>
              <div>↕ {bus.headway_ahead_s}s / {bus.headway_behind_s}s</div>
            </div>
          </Tooltip>
        </Marker>
      ))}
    </MapContainer>
  )
}
