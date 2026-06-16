import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

st.set_page_config(
page_title="Safe Radius Map",
page_icon="🛡️",
layout="wide"
)

st.title("🛡️ Safe Radius Map")
st.caption("반경 1km 내 경찰서·소방서를 확인하여 주변 안전도를 파악합니다.")

# --------------------------------

# 위치 검색

# --------------------------------

location_name = st.text_input(
"지역 검색",
"Cheonan, South Korea"
)

# --------------------------------

# 주소 → 좌표

# --------------------------------

@st.cache_data
def geocode(place):
try:
geo = Nominatim(user_agent="safe_radius_map")
loc = geo.geocode(place, timeout=10)

```
    if loc:
        return loc.latitude, loc.longitude

    return None

except:
    return None
```

# --------------------------------

# Overpass API

# --------------------------------

@st.cache_data(ttl=3600)
def get_safety_places(lat, lon):

```
query = f"""
[out:json];
(
  node["amenity"="police"](around:1000,{lat},{lon});
  node["amenity"="fire_station"](around:1000,{lat},{lon});
);
out;
"""

try:

    response = requests.get(
        "https://overpass-api.de/api/interpreter",
        params={"data": query},
        timeout=20
    )

    data = response.json()

    result = []

    for item in data.get("elements", []):

        result.append({
            "name": item.get("tags", {}).get("name", "이름 없음"),
            "type": item.get("tags", {}).get("amenity"),
            "lat": item["lat"],
            "lon": item["lon"]
        })

    return result

except:
    return []
```

coords = geocode(location_name)

if not coords:
st.error("위치를 찾을 수 없습니다.")
st.stop()

lat, lon = coords

places = get_safety_places(lat, lon)

police = [x for x in places if x["type"] == "police"]
fire = [x for x in places if x["type"] == "fire_station"]

# --------------------------------

# 거리 계산

# --------------------------------

def nearest_distance(items):

```
if not items:
    return None

distances = []

for item in items:

    d = geodesic(
        (lat, lon),
        (item["lat"], item["lon"])
    ).meters

    distances.append(d)

return min(distances)
```

nearest_police = nearest_distance(police)
nearest_fire = nearest_distance(fire)

facility_count = len(police) + len(fire)

# --------------------------------

# 안전등급

# --------------------------------

if facility_count >= 10:
grade = "매우 안전 🟢"

elif facility_count >= 5:
grade = "안전 🟢"

elif facility_count >= 2:
grade = "보통 🟡"

else:
grade = "주의 🔴"

# --------------------------------

# 통계

# --------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric("👮 경찰서", len(police))
c2.metric("🚒 소방서", len(fire))
c3.metric("🏆 안전등급", grade)

if nearest_police:
c4.metric(
"가장 가까운 경찰서",
f"{nearest_police:.0f}m"
)
else:
c4.metric(
"가장 가까운 경찰서",
"-"
)

# --------------------------------

# 지도

# --------------------------------

m = folium.Map(
location=[lat, lon],
zoom_start=15
)

# 현재 위치

folium.Marker(
[lat, lon],
tooltip="검색 위치",
icon=folium.Icon(color="blue")
).add_to(m)

# 반경 1km

folium.Circle(
location=[lat, lon],
radius=1000,
color="blue",
fill=False
).add_to(m)

# 경찰서

for p in police:

```
distance = geodesic(
    (lat, lon),
    (p["lat"], p["lon"])
).meters

folium.Marker(
    [p["lat"], p["lon"]],
    tooltip=f"{p['name']} ({distance:.0f}m)",
    icon=folium.Icon(color="green")
).add_to(m)
```

# 소방서

for f in fire:

```
distance = geodesic(
    (lat, lon),
    (f["lat"], f["lon"])
).meters

folium.Marker(
    [f["lat"], f["lon"]],
    tooltip=f"{f['name']} ({distance:.0f}m)",
    icon=folium.Icon(color="orange")
).add_to(m)
```

st_folium(
m,
width=None,
height=650
)

# --------------------------------

# 목록

# --------------------------------

st.subheader("📋 반경 1km 내 안전시설")

if places:

```
rows = []

for p in places:

    d = geodesic(
        (lat, lon),
        (p["lat"], p["lon"])
    ).meters

    rows.append({
        "시설명": p["name"],
        "종류": "경찰서" if p["type"] == "police" else "소방서",
        "거리(m)": round(d)
    })

df = pd.DataFrame(rows)

st.dataframe(
    df.sort_values("거리(m)"),
    use_container_width=True
)
```

else:
st.warning("반경 1km 내 안전시설이 없습니다.")
