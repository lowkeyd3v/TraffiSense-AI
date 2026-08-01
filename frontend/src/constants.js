// Shared constants and helpers for the Traffic Intelligence Engine

export const API = import.meta.env.PROD ? '' : 'http://127.0.0.1:8000'

export const EVENT_CAUSES = [
  'vehicle_breakdown','accident','water_logging','tree_fall','pot_holes',
  'congestion','construction','public_event','procession','protest',
  'vip_movement','road_conditions','others'
]

export const VEH_TYPES = [
  'heavy_vehicle','lcv','bmtc_bus','private_bus','private_car',
  'ksrtc_bus','truck','auto','taxi','others','unknown'
]

export const CORRIDORS = [
  'Non-corridor','Mysore Road','Bellary Road 1','Bellary Road 2',
  'Tumkur Road','Hosur Road','Magadi Road','ORR East 1','ORR East 2',
  'ORR North 1','ORR North 2','Old Madras Road'
]

export const CAUSE_LABELS = {
  vehicle_breakdown: 'Vehicle Breakdown', accident: 'Accident',
  water_logging: 'Water Logging', tree_fall: 'Tree Fall',
  pot_holes: 'Pot Holes', congestion: 'Congestion',
  construction: 'Construction', public_event: 'Public Event',
  procession: 'Procession', protest: 'Protest',
  vip_movement: 'VIP Movement', road_conditions: 'Road Conditions',
  others: 'Others'
}

export const RISK_CONFIG = {
  Critical: { cls: 'risk-critical', dot: '#ef4444' },
  High:     { cls: 'risk-high',     dot: '#f59e0b' },
  Medium:   { cls: 'risk-medium',   dot: '#f97316' },
  Low:      { cls: 'risk-low',      dot: '#10b981' },
}

export function fmt(n, unit='') {
  if (n == null) return '—'
  return `${Math.round(n)}${unit}`
}
