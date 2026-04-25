from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="CampusPark Smart Monitor",
    page_icon="🅿️",
    layout="wide",
)

# -----------------------------
# Styling (FIXED)
# -----------------------------
st.markdown("""
<style>
.main {background-color: #f6f8fb;}

.app-title {
    font-size: 2rem;
    font-weight: 800;
    color: #12324a;
}

.subtitle {
    color: #5b6777;
    margin-bottom: 1rem;
}

.metric-card {
    background: white;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
}

.metric-value {
    font-size: 1.8rem;
    font-weight: bold;
}

.spot-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
}

.spot {
    padding: 10px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
}

.empty {background: #c9f7d1;}
.occupied {background: #ffd5d5;}
.reserved {background: #ffe9b8;}
.best {border: 3px solid green;}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Data Models
# -----------------------------
@dataclass
class ParkingSpot:
    spot_id: str
    status: str
    distance: int


@dataclass
class ParkingZone:
    zone_id: str
    name: str
    x: int
    y: int
    spots: List[ParkingSpot]


USER_LOCATIONS = {
    "Main Gate": (0, 0),
    "Engineering Block": (8, 2),
    "Library": (2, 4),
}

# -----------------------------
# Functions
# -----------------------------
def generate_data():
    zones = []
    for z in range(3):
        spots = []
        for i in range(15):
            status = random.choice(["empty", "occupied", "reserved"])
            spots.append(ParkingSpot(f"{z}-{i}", status, random.randint(30, 200)))
        zones.append(ParkingZone(str(z), f"Zone {z}", z*3, z*2, spots))
    return zones


def best_spot(zones):
    candidates = []
    for zone in zones:
        for s in zone.spots:
            if s.status == "empty":
                score = s.distance
                candidates.append((score, zone, s))
    if not candidates:
        return None
    return sorted(candidates)[0]


# -----------------------------
# App
# -----------------------------
zones = generate_data()

st.markdown(
    '<div class="app-title">CampusPark Smart Monitor</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Smart parking dashboard</div>',
    unsafe_allow_html=True
)

best = best_spot(zones)

# -----------------------------
# Display zones
# -----------------------------
for zone in zones:
    st.markdown(f"### {zone.name}")

    html = '<div class="spot-grid">'

    for s in zone.spots:
        cls = s.status
        extra = " best" if best and s == best[2] else ""

        html += f"""
        <div class="spot {cls}{extra}">
            {s.spot_id}<br>{s.status}
        </div>
        """

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


# -----------------------------
# Best spot
# -----------------------------
st.markdown("### Best Spot")

if best:
    st.success(f"Recommended: {best[2].spot_id} in {best[1].name}")
else:
    st.error("No available spots")
