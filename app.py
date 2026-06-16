import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2

st.set_page_config(
page_title="안전구역 지도",
page_icon="🛡️",
layout="wide"
)

st.title("🛡️ 안전구역 지도")
st.caption("반경 1km 내 경찰서·소방서 기반 안전도 분석")

# --------------------------------

# 거리 계산

# --------------------------------

def distance_m(lat1, lon1, lat2, lon2):

```
R = 6371000

dlat = radians(lat2 - lat1)
dlon = radians(lon2 - lon1)

a = (
    sin(dlat / 2) ** 2
    + cos(radians(lat1))
    * cos(radians(lat2))
    * sin(dlon / 2) ** 2
)

c = 2 * atan2(sqrt(a), sqrt(1 - a))

return R * c
```

# --------------------------------

# 도시 데이터

# --------------------------------

cities = {
"서울": (37.5665, 126.9780),
"부산": (35.1796, 129.0756),
"대구": (35.8714, 128.6014),
"인천": (37.4563, 126.7052),
"대전": (36.3504, 127.3845),
"광주": (35.1595, 126.8526),
"울산": (35.5384, 129.3114),
"천안": (36.8151, 127.1139)
}

# --------------------------------

# 경찰서 / 소방서 샘플 데이터

# --------------------------------

facilities = pd.DataFrame([

```
["서울중부경찰서","경찰서",37.5636,126.9890],
["서울남대문경찰서","경찰서",37.5585,126.9772],
["서울종로소방서","소방서",37.5734,126.9790],

["부산중부경찰서","경찰서",35.1068,129.0325],
["부산동부소방서","소방서",35.1373,129.0930],

["대구중부경찰서","경찰서",35.8694,128.5932],
["대구중부소방서","소방서",35.8712,128.5961],

["인천중부경찰서","경찰서",37.4734,126.6212],
["인천중부소방서","소방서",37.4701,126.6333],

["대전중부경찰서","경찰서",36.3286,127.4238],
["대전중부소방서","소방서",36.3270,127.4214],

["광주동부경찰서","경찰서",35.1464,126.9236],
["광주소방안전본부","소방서",35.1608,126.8805],

["울산중부경찰서","경찰서",35.5570,129.3208],
["울산중부소방서","소방서",35.5532,129.3191],

["천안동남경찰서","경찰서",36.8064,127.1522],
["천안서북소방서","소방서",36.8288,127.1227]
```

], columns=["이름","종류","위도","경도"])

# --------------------------------

# 도시 선택

# --------------------------------

city = st.sidebar.selectbox(
"도시 선택",
list(cities.keys())
)

base_lat, base_lon = cities[city]

# --------------------------------

# 거리 계산

# --------------------------------

distances = []

for _, row in facilities.iterrows():

```
d = distance_m(
    base_lat,
    base_lon,
    row["위도"],
    row["경도"]
)

distances.append(d)
```

facilities["거리"] = distances

near = facilities[
facilities["거리"] <= 1000
]

police_count = len(
near[near["종류"]=="경찰서"]
)

fire_count = len(
near[near["종류"]=="소방서"]
)

total = len(near)

# --------------------------------

# 안전등급

# --------------------------------

if total >= 5:
grade = "매우 안전 🟢"
elif total >= 3:
grade = "안전 🟢"
elif total >= 1:
grade = "보통 🟡"
else:
grade = "주의 🔴"

# --------------------------------

# 통계

# --------------------------------

c1,c2,c3,c4 = st.columns(4)

c1.metric("👮 경찰서", police_count)
c2.metric("🚒 소방서", fire_count)
c3.metric("🏢 안전시설", total)
c4.metric("🏆 안전등급", grade)

# --------------------------------

# 지도

# --------------------------------

m = folium.Map(
location=[base_lat, base_lon],
zoom_start=14
)

folium.Marker(
[base_lat, base_lon],
tooltip=f"{city} 중심",
icon=folium.Icon(color="blue")
).add_to(m)

folium.Circle(
location=[base_lat, base_lon],
radius=1000,
color="blue",
fill=False
).add_to(m)

for _, row in near.iterrows():

```
color = "green"

if row["종류"] == "소방서":
    color = "orange"

folium.Marker(
    [row["위도"], row["경도"]],
    tooltip=f"{row['이름']} ({row['거리']:.0f}m)",
    icon=folium.Icon(color=color)
).add_to(m)
```

st_folium(
m,
width=None,
height=600
)

st.subheader("📋 반경 1km 내 시설")

if len(near) > 0:

```
st.dataframe(
    near[["이름","종류","거리"]]
    .sort_values("거리"),
    use_container_width=True
)
```

else:

```
st.warning("반경 1km 내 시설이 없습니다.")
```
