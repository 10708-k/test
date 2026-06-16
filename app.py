import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
import requests

st.set_page_config(
    page_title="Safe Zone Map",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Safe Zone Map")
st.caption("주변 안전구역(경찰서·소방서)과 위험구역을 지도에서 확인하세요.")

# ----------------------------
# 위험구역 세션 상태
# ----------------------------
if "danger_zones" not in st.session_state:
    st.session_state.danger_zones = []

# ----------------------------
# 지역 검색
# ----------------------------
st.sidebar.header("📍 지역 검색")

location_name = st.sidebar.text_input(
    "지역 입력",
    value="Cheonan, South Korea"
)

# ----------------------------
# 좌표 변환
# ----------------------------
@st.cache_data(show_spinner=False)
def geocode_location(place):
    try:
        geolocator = Nominatim(user_agent="safe_zone_map")
        location = geolocator.geocode(place, timeout=10)

        if location:
            return location.latitude, location.longitude

        return None

    except GeocoderServiceError:
        return None
    except Exception:
        return None


# ----------------------------
# Overpass API
# ----------------------------
@st.cache_data(ttl=3600)
def get_safe_places(lat, lon):
    query = f"""
    [out:json];
    (
      node["amenity"="police"](around:5000,{lat},{lon});
      node["amenity"="fire_station"](around:5000,{lat},{lon});
    );
    out;
    """

    url = "https://overpass-api.de/api/interpreter"

    try:
        response = requests.get(
            url,
            params={"data": query},
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        places = []

        for item in data.get("elements", []):

            amenity = item.get("tags", {}).get("amenity", "")
            name = item.get("tags", {}).get("name", "이름 없음")

            places.append(
                {
                    "name": name,
                    "type": amenity,
                    "lat": item["lat"],
                    "lon": item["lon"],
                }
            )

        return places

    except Exception:
        return []


# ----------------------------
# 위치 검색
# ----------------------------
coords = geocode_location(location_name)

if not coords:
    st.error("지역을 찾을 수 없습니다.")
    st.stop()

lat, lon = coords

# ----------------------------
# 위험구역 등록
# ----------------------------
st.sidebar.header("⚠️ 위험구역 추가")

danger_name = st.sidebar.text_input(
    "위험구역 이름",
    placeholder="어두운 골목"
)

if st.sidebar.button("위험구역 등록"):

    st.session_state.danger_zones.append(
        {
            "name": danger_name if danger_name else "위험 신고 지점",
            "lat": lat,
            "lon": lon,
        }
    )

    st.sidebar.success("등록 완료")

# ----------------------------
# 안전구역 조회
# ----------------------------
with st.spinner("안전구역 검색 중..."):
    safe_places = get_safe_places(lat, lon)

# ----------------------------
# 통계
# ----------------------------
police_count = len(
    [x for x in safe_places if x["type"] == "police"]
)

fire_count = len(
    [x for x in safe_places if x["type"] == "fire_station"]
)

danger_count = len(st.session_state.danger_zones)

score = max(
    0,
    min(
        100,
        50 + (police_count * 5) + (fire_count * 5) - (danger_count * 10)
    )
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("👮 경찰서", police_count)
col2.metric("🚒 소방서", fire_count)
col3.metric("⚠️ 위험구역", danger_count)
col4.metric("🛡️ 안전도", f"{score}/100")

# ----------------------------
# 지도 생성
# ----------------------------
m = folium.Map(
    location=[lat, lon],
    zoom_start=14
)

# 현재 위치
folium.Marker(
    [lat, lon],
    tooltip="검색 위치",
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(m)

# 경찰서
for place in safe_places:

    if place["type"] == "police":

        folium.Marker(
            [place["lat"], place["lon"]],
            tooltip=place["name"],
            popup=f"👮 {place['name']}",
            icon=folium.Icon(color="green")
        ).add_to(m)

# 소방서
for place in safe_places:

    if place["type"] == "fire_station":

        folium.Marker(
            [place["lat"], place["lon"]],
            tooltip=place["name"],
            popup=f"🚒 {place['name']}",
            icon=folium.Icon(color="orange")
        ).add_to(m)

# 위험구역
for danger in st.session_state.danger_zones:

    folium.CircleMarker(
        location=[danger["lat"], danger["lon"]],
        radius=10,
        color="red",
        fill=True,
        fill_color="red",
        popup=f"⚠️ {danger['name']}"
    ).add_to(m)

st_folium(
    m,
    width=None,
    height=650
)

# ----------------------------
# 상세 목록
# ----------------------------
st.subheader("📋 안전구역 목록")

if safe_places:

    df = pd.DataFrame(safe_places)

    df["type"] = df["type"].replace(
        {
            "police": "경찰서",
            "fire_station": "소방서"
        }
    )

    st.dataframe(
        df[["name", "type"]],
        use_container_width=True
    )

else:
    st.warning("검색된 안전구역이 없습니다.")

# ----------------------------
# 위험구역 목록
# ----------------------------
st.subheader("⚠️ 위험구역 목록")

if st.session_state.danger_zones:

    st.dataframe(
        pd.DataFrame(st.session_state.danger_zones)[["name"]],
        use_container_width=True
    )

else:
    st.info("등록된 위험구역이 없습니다.")
