from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List

import streamlit as st


st.set_page_config(
    page_title="CampusPark Smart Monitor",
    page_icon="🅿️",
    layout="wide",
)


st.markdown(
    """
<style>
.app-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #12324a;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: #5b6777;
    margin-bottom: 1.5rem;
}

.spot-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 25px;
}

.spot {
    border-radius: 14px;
    min-height: 80px;
    padding: 10px;
    font-weight: 800;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.empty {
    background-color: #c9f7d1;
}

.occupied {
    background-color: #ffd5d5;
}

.reserved {
    background-color: #ffe9b8;
}

.best {
    border: 4px solid #0f5c35;
}

.metric-box {
    background: white;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    border: 1px solid #edf1f5;
    margin-bottom: 20px;
}
</style>
""",
    unsafe_allow_html=True,
)


@dataclass
class ParkingSpot:
    spot_id: str
    status: str
    distance_m: int


@dataclass
class ParkingZone:
    zone_id: str
    name: str
    spots: List[ParkingSpot]


def generate_data() -> List[ParkingZone]:
    random.seed(7)

    zones = []

    zone_names = [
        "North Parking",
        "Central Parking",
        "Engineering Parking",
        "Library Parking",
        "Medical Parking",
    ]

    for z, name in enumerate(zone_names):
        spots = []

        for i in range(1, 16):
            status = random.choices(
                ["empty", "occupied", "reserved"],
                weights=[0.35, 0.55, 0.10],
                k=1,
            )[0]

            spots.append(
                ParkingSpot(
                    spot_id=f"{chr(65 + z)}-{i:02d}",
                    status=status,
                    distance_m=random.randint(30, 250),
                )
            )

        zones.append(
            ParkingZone(
                zone_id=chr(65 + z),
                name=name,
                spots=spots,
            )
        )

    return zones


def find_best_spot(zones: List[ParkingZone]):
    empty_spots = []

    for zone in zones:
        for spot in zone.spots:
            if spot.status == "empty":
                empty_spots.append((spot.distance_m, zone, spot))

    if not empty_spots:
        return None

    return sorted(empty_spots, key=lambda x: x[0])[0]


def status_icon(status: str) -> str:
    if status == "empty":
        return "🟢"
    if status == "occupied":
        return "🔴"
    return "🟡"


def render_zone(zone: ParkingZone, best_spot_id: str | None):
    html = '<div class="spot-grid">'

    for spot in zone.spots:
        best_class = " best" if spot.spot_id == best_spot_id else ""

        html += (
            f'<div class="spot {spot.status}{best_class}">'
            f'<div>{spot.spot_id}</div>'
            f'<div>{status_icon(spot.status)} {spot.status.title()}</div>'
            f'</div>'
        )

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


zones = generate_data()
best = find_best_spot(zones)

st.markdown(
    '<div class="app-title">CampusPark Smart Monitor</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Smart parking dashboard for real-time availability and best-spot recommendation.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Controls")
    selected_location = st.selectbox(
        "Current user location",
        ["Main Gate", "Library", "Engineering Block", "Medical College", "Student Center"],
    )

    selected_zone = st.selectbox(
        "Selected parking zone",
        [zone.name for zone in zones],
    )

    if st.button("🔄 Refresh live data"):
        st.rerun()

    st.markdown("---")
    st.markdown("### Suggested full system stack")
    st.write("**Frontend:** Streamlit")
    st.write("**Backend:** FastAPI / Flask")
    st.write("**Database:** PostgreSQL")
    st.write("**IoT:** ESP32 + sensors")
    st.write("**AI:** YOLO / OpenCV")

total_spots = sum(len(zone.spots) for zone in zones)
available_spots = sum(
    1 for zone in zones for spot in zone.spots if spot.status == "empty"
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f'<div class="metric-box"><h4>Total Parking Capacity</h4><h2>{total_spots}</h2></div>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f'<div class="metric-box"><h4>Available Spots</h4><h2>{available_spots}</h2></div>',
        unsafe_allow_html=True,
    )

with c3:
    if best:
        st.markdown(
            f'<div class="metric-box"><h4>Best Spot</h4><h2>{best[2].spot_id}</h2></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="metric-box"><h4>Best Spot</h4><h2>None</h2></div>',
            unsafe_allow_html=True,
        )

st.markdown("## Smart Parking Visualization Map")

st.markdown(
    "🟢 Empty &nbsp;&nbsp; 🔴 Occupied &nbsp;&nbsp; 🟡 Reserved &nbsp;&nbsp; ⭐ Best Spot",
    unsafe_allow_html=True,
)

best_spot_id = best[2].spot_id if best else None

for zone in zones:
    st.markdown(f"### {zone.name}")
    render_zone(zone, best_spot_id)

st.markdown("## Best Available Spot")

if best:
    distance, zone, spot = best
    st.success(f"Recommended spot: {spot.spot_id}")
    st.write(f"**Zone:** {zone.name}")
    st.write(f"**Distance:** {distance} m")
else:
    st.error("No empty spots available right now.")
