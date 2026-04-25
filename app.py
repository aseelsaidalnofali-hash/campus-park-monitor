from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st


# -----------------------------
# Configuration
# -----------------------------
st.set_page_config(
    page_title="CampusPark Smart Monitor",
    page_icon="🅿️",
    layout="wide",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #f6f8fb;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
    }

    .app-title {
        font-size: 2rem;
        font-weight: 800;
        color: #12324a;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #5b6777;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: white;
        border-radius: 18px;
        padding: 18px 18px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
        border: 1px solid #edf1f5;
        min-height: 112px;
    }

    .metric-label {
        color: #61707f;
        font-size: 0.95rem;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #18354b;
        line-height: 1.15;
    }

    .metric-sub {
        color: #6d7b88;
        margin-top: 0.45rem;
        font-size: 0.92rem;
    }

    .panel {
        background: white;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
        border: 1px solid #edf1f5;
    }

    .panel-title {
        font-size: 1.1rem;
        font-weight: 750;
        color: #18354b;
        margin-bottom: 0.8rem;
    }

    .legend-chip {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 999px;
        margin-right: 8px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .spot-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 10px;
        margin-top: 14px;
    }

    .spot {
        border-radius: 12px;
        min-height: 64px;
        padding: 8px;
        color: #0f1720;
        font-weight: 700;
        font-size: 0.85rem;
        display: flex;
        align-items: end;
        justify-content: space-between;
        border: 2px solid rgba(0,0,0,0.05);
    }

    .spot-empty {
        background: #c9f7d1;
    }

    .spot-occupied {
        background: #ffd5d5;
    }

    .spot-reserved {
        background: #ffe9b8;
    }

    .spot-best {
        border: 3px solid #144a33 !important;
        box-shadow: 0 0 0 4px rgba(26, 140, 76, 0.12);
    }

    .zone-card {
        background: #fbfcfe;
        border: 1px solid #edf1f5;
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 12px;
    }

    .best-label {
        background: #e6fff0;
        color: #0f5c35;
        font-weight: 800;
        padding: 8px 12px;
        border-radius: 999px;
        display: inline-block;
        margin-top: 8px;
        font-size: 0.92rem;
    }

    .small-note {
        color: #657383;
        font-size: 0.88rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Domain model
# -----------------------------
@dataclass
class ParkingSpot:
    spot_id: str
    status: str  # "empty", "occupied", "reserved"
    sensor_id: str
    distance_m: int


@dataclass
class ParkingZone:
    zone_id: str
    name: str
    x: int
    y: int
    spots: List[ParkingSpot]


USER_LOCATIONS: Dict[str, Tuple[int, int]] = {
    "Main Gate": (0, 0),
    "Library": (2, 4),
    "Engineering Block": (8, 2),
    "Medical College": (10, 7),
    "Student Center": (4, 8),
}

AVERAGE_SPEED_M_PER_MIN = 90  # walking + internal vehicle mix


def initialize_data() -> List[ParkingZone]:
    random.seed(7)
    zone_names = [
        ("A", "North Parking"),
        ("B", "Central Parking"),
        ("C", "Engineering Parking"),
        ("D", "Library Parking"),
        ("E", "Medical Parking"),
    ]
    coordinates = {
        "A": (2, 1),
        "B": (5, 2),
        "C": (8, 2),
        "D": (3, 6),
        "E": (9, 7),
    }

    zones: List[ParkingZone] = []
    for zone_id, name in zone_names:
        zx, zy = coordinates[zone_id]
        spots: List[ParkingSpot] = []
        for i in range(1, 16):
            status = random.choices(
                ["empty", "occupied", "reserved"],
                weights=[0.32, 0.58, 0.10],
                k=1,
            )[0]
            spots.append(
                ParkingSpot(
                    spot_id=f"{zone_id}-{i:02d}",
                    status=status,
                    sensor_id=f"SENSOR-{zone_id}-{100+i}",
                    distance_m=random.randint(35, 240),
                )
            )
        zones.append(ParkingZone(zone_id=zone_id, name=name, x=zx, y=zy, spots=spots))
    return zones


def refresh_statuses(zones: List[ParkingZone]) -> None:
    """Simulate real-time IoT updates from parking sensors/cameras."""
    for zone in zones:
        for spot in zone.spots:
            roll = random.random()
            if roll < 0.08:
                if spot.status == "occupied":
                    spot.status = "empty"
                elif spot.status == "empty":
                    spot.status = "occupied"
            elif roll < 0.1:
                spot.status = "reserved"


def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def compute_zone_eta_minutes(user_xy: Tuple[int, int], zone: ParkingZone) -> int:
    grid_distance = manhattan_distance(user_xy, (zone.x, zone.y))
    approx_meters = grid_distance * 120
    eta = max(1, round(approx_meters / AVERAGE_SPEED_M_PER_MIN))
    return eta


def zone_summary(zone: ParkingZone) -> Dict[str, int]:
    empty_count = sum(1 for s in zone.spots if s.status == "empty")
    occupied_count = sum(1 for s in zone.spots if s.status == "occupied")
    reserved_count = sum(1 for s in zone.spots if s.status == "reserved")
    total = len(zone.spots)
    return {
        "total": total,
        "empty": empty_count,
        "occupied": occupied_count,
        "reserved": reserved_count,
    }


def find_best_spot(user_xy: Tuple[int, int], zones: List[ParkingZone]) -> Dict[str, object] | None:
    candidates = []
    for zone in zones:
        eta = compute_zone_eta_minutes(user_xy, zone)
        for spot in zone.spots:
            if spot.status == "empty":
                score = (eta * 0.55) + (spot.distance_m / 100 * 0.45)
                candidates.append(
                    {
                        "zone": zone,
                        "spot": spot,
                        "eta": eta,
                        "score": score,
                    }
                )
    if not candidates:
        return None
    return sorted(candidates, key=lambda x: (x["score"], x["eta"], x["spot"].distance_m))[0]


def render_metric(label: str, value: str, sub: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_zone_grid(zone: ParkingZone, best_spot_id: str | None) -> None:
    blocks = []
    for spot in zone.spots:
        spot_class = {
            "empty": "spot-empty",
            "occupied": "spot-occupied",
            "reserved": "spot-reserved",
        }[spot.status]
        extra = " spot-best" if spot.spot_id == best_spot_id else ""
        icon = {
            "empty": "🟢",
            "occupied": "🔴",
            "reserved": "🟡",
        }[spot.status]
        blocks.append(
            f"""
            <div class="spot {spot_class}{extra}">
                <div>{spot.spot_id}</div>
                <div>{icon}</div>
            </div>
            """
        )

    st.markdown(
        f"""
        <div class="spot-grid">
            {''.join(blocks)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    if "zones" not in st.session_state:
        st.session_state.zones = initialize_data()

    st.markdown('<div class="app-title">CampusPark Smart Monitor</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Smart parking dashboard for a university campus with real-time availability, ETA, and best-spot recommendation.</div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Controls")
        selected_location_name = st.selectbox("Current user location", list(USER_LOCATIONS.keys()), index=1)
        selected_zone_id = st.selectbox(
            "Selected parking zone",
            [z.zone_id for z in st.session_state.zones],
            index=1,
            format_func=lambda zid: next(z.name for z in st.session_state.zones if z.zone_id == zid),
        )

        live_refresh = st.button("🔄 Refresh live data")

        st.markdown("---")
        st.markdown("### Suggested full system stack")
        st.caption(
            """
            **Frontend:** Streamlit / Dash / React  
            **Backend:** FastAPI / Flask  
            **Database:** PostgreSQL  
            **IoT:** ESP32 + ultrasonic sensors / cameras  
            **Analytics:** Pandas + Python  
            **Optional AI:** YOLO/OpenCV + plate recognition
            """
        )

    if live_refresh:
        refresh_statuses(st.session_state.zones)

    selected_zone = next(z for z in st.session_state.zones if z.zone_id == selected_zone_id)
    selected_user_xy = USER_LOCATIONS[selected_location_name]
    best = find_best_spot(selected_user_xy, st.session_state.zones)

    total_spots = sum(len(z.spots) for z in st.session_state.zones)
    total_empty = sum(zone_summary(z)["empty"] for z in st.session_state.zones)
    selected_zone_eta = compute_zone_eta_minutes(selected_user_xy, selected_zone)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric("Total Parking Capacity", str(total_spots), "Across all campus zones")
    with c2:
        render_metric("Available Spots", str(total_empty), "Real-time sensor-based count")
    with c3:
        render_metric("Selected Zone", selected_zone.name, f"Zone {selected_zone.zone_id}")
    with c4:
        render_metric("Expected Time to Arrival", f"{selected_zone_eta} min", f"ETA to {selected_zone.name}")

    left, right = st.columns([1.9, 1.1])

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Smart Parking Visualization Map</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <span class="legend-chip" style="background:#c9f7d1;">🟢 Empty</span>
            <span class="legend-chip" style="background:#ffd5d5;">🔴 Occupied</span>
            <span class="legend-chip" style="background:#ffe9b8;">🟡 Reserved</span>
            <span class="legend-chip" style="background:#e6fff0;border:1px solid #0f5c35;">⭐ Best Spot</span>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="small-note">Empty spots are highlighted in green so users can quickly identify the nearest available slot at a glance.</div>',
            unsafe_allow_html=True,
        )

        best_spot_id = best["spot"].spot_id if best else None

        for zone in st.session_state.zones:
            summary = zone_summary(zone)
            eta = compute_zone_eta_minutes(selected_user_xy, zone)
            is_best_zone = best is not None and best["zone"].zone_id == zone.zone_id

            st.markdown(
                f"""
                <div class="zone-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap;">
                        <div>
                            <div style="font-size:1rem; font-weight:800; color:#18354b;">{zone.name}</div>
                            <div class="small-note">
                                Available: {summary["empty"]} / {summary["total"]} &nbsp;|&nbsp;
                                Occupied: {summary["occupied"]} &nbsp;|&nbsp;
                                Reserved: {summary["reserved"]}
                            </div>
                        </div>
                        <div style="font-weight:700; color:#12324a;">ETA: {eta} min</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_zone_grid(zone, best_spot_id if is_best_zone else None)

        if best:
            st.markdown(
                f'<div class="best-label">Best Spot → {best["eta"]} min away</div>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Best Available Spot</div>', unsafe_allow_html=True)

        if best:
            best_zone = best["zone"]
            best_spot = best["spot"]
            st.success(f"Recommended spot: {best_spot.spot_id}")
            st.write(f"**Zone:** {best_zone.name}")
            st.write(f"**ETA:** {best['eta']} min")
            st.write(f"**Distance inside zone:** {best_spot.distance_m} m")
            st.write("**Selection logic:** distance + live availability + ETA")
        else:
            st.error("No empty spots available right now.")

        st.markdown("---")
        st.markdown("#### Zone details")
        for zone in st.session_state.zones:
            summary = zone_summary(zone)
            eta = compute_zone_eta_minutes(selected_user_xy, zone)
            with st.expander(f"{zone.name} • ETA {eta} min"):
                st.write(f"**Total spots:** {summary['total']}")
                st.write(f"**Available spots:** {summary['empty']}")
                st.write(f"**Occupied spots:** {summary['occupied']}")
                st.write(f"**Reserved spots:** {summary['reserved']}")

        st.markdown("---")
        st.markdown("#### Practical system architecture")
        st.caption(
            """
            1. **IoT layer:** ultrasonic sensors or cameras detect each slot state.  
            2. **Edge layer:** ESP32/Raspberry Pi preprocesses data.  
            3. **API layer:** FastAPI receives live occupancy updates.  
            4. **Data layer:** PostgreSQL stores zones, slots, trips, and history.  
            5. **Dashboard layer:** campus staff and drivers view live parking and ETA.  
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Suggested database schema")
    db_df = pd.DataFrame(
        [
            ["parking_zones", "zone_id, zone_name, center_x, center_y, total_capacity"],
            ["parking_spots", "spot_id, zone_id, sensor_id, status, distance_m"],
            ["vehicles", "vehicle_id, license_plate, owner_type"],
            ["parking_events", "event_id, spot_id, vehicle_id, entry_time, exit_time"],
            ["reservations", "reservation_id, user_id, spot_id, reserved_from, reserved_to"],
            ["users", "user_id, name, role, current_location"],
        ],
        columns=["Table", "Core Columns"],
    )
    st.dataframe(db_df, use_container_width=True, hide_index=True)

    st.markdown("### Detection algorithm idea")
    st.code(
        """
For each parking spot:
    Read sensor/camera input
    If object detected inside threshold:
        status = OCCUPIED
    Else if reserved flag active:
        status = RESERVED
    Else:
        status = EMPTY

For best spot recommendation:
    For each EMPTY spot:
        eta = compute_eta(user_location, zone_location)
        score = (0.55 * eta) + (0.45 * internal_distance)
    Return spot with minimum score
        """.strip(),
        language="python",
    )

    st.markdown("### UI/UX notes")
    st.info(
        """
        - Keep the top row for fast-scan KPIs.  
        - Use green for empty slots to reduce search time.  
        - Show ETA both globally and inside each zone detail.  
        - Keep the best-spot label short and visible: **Best Spot → 3 min away**.  
        - Use a clean grid map so students and visitors understand it instantly.
        """
    )


if __name__ == "__main__":
    main()
