import json
from pathlib import Path
from typing import Dict, List

EXTRAS_PATH = Path(__file__).resolve().parent / "database" / "network_config_extras.json"


def _normalize_interfaces(values: List[str] | None) -> List[str]:
    if not values:
        return []

    parsed: List[str] = []
    seen = set()
    for raw in values:
        value = str(raw or "").strip()
        if value and value not in seen:
            seen.add(value)
            parsed.append(value)
    return parsed


def _normalize_zone_map(zone_map: Dict[str, str] | None) -> Dict[str, str]:
    if not zone_map:
        return {}

    allowed = {"wan", "lan", "wlan"}
    normalized: Dict[str, str] = {}
    for iface, zone in zone_map.items():
        iface_key = str(iface or "").strip()
        zone_value = str(zone or "").strip().lower()
        if iface_key and zone_value in allowed:
            normalized[iface_key] = zone_value
    return normalized


def load_network_extras() -> Dict[str, object]:
    if not EXTRAS_PATH.exists():
        return {"capture_interfaces": [], "zone_map": {}}

    try:
        raw = json.loads(EXTRAS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"capture_interfaces": [], "zone_map": {}}

    capture_interfaces = _normalize_interfaces(raw.get("capture_interfaces", []))
    zone_map = _normalize_zone_map(raw.get("zone_map", {}))

    return {
        "capture_interfaces": capture_interfaces,
        "zone_map": zone_map,
    }


def save_network_extras(capture_interfaces: List[str] | None, zone_map: Dict[str, str] | None) -> None:
    payload = {
        "capture_interfaces": _normalize_interfaces(capture_interfaces),
        "zone_map": _normalize_zone_map(zone_map),
    }

    EXTRAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXTRAS_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
