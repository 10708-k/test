import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Safety Map Explorer",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Safety Map Explorer")
st.caption("안전 지역과 위험 지역을 지도에서 확인하세요.")

# 예제 데이터
data = [
    {
        "지역": "서울역",
        "위도": 37.5547,
        "경도": 126.9706,
        "등급": "위험",
        "설명": "야간 범죄 신고 다수"
    },
    {
        "지역": "광화문",
        "위도": 37.5759,
        "경도": 126.9768,
        "등급": "안전",
        "설명": "유동인구 많고 치안 우수"
    },
    {
        "지역": "강남역",
        "위도": 37.4979,
        "경도": 127.0276,
        "등급": "주의",
        "설명": "야간 혼잡 지역"
    },
    {
        "지역": "잠실",
        "위도": 37.5133,
        "경도": 127.1002,
        "등급": "안전",
        "설명": "주거 및 상업지역"
    },
    {
        "지역": "구로디지털단지",
        "위도": 37.4850,
        "경도": 126.9019,
        "등급": "위험",
        "설명": "야간 신고 증가 지역"
    },
    {
        "지역": "홍대입구",
        "위도": 37.5572,
        "경도": 126.9254,
        "등급": "주의",
        "설명": "심야 혼잡 지역"
    }
]

df = pd.DataFrame(data)

st.sidebar.header("필터")

risk_filter = st.sidebar.selectbox(
    "위험도 선택",
    ["전체", "안전", "주의", "위험"]
)

if risk_filter != "전체":
    filtered_df = df[df["등급"] == risk_filter]
else:
    filtered_df = df.copy()

# 통계
col1, col2, col3, col4 = st.columns(4)

col1.metric("전체", len(df))
col2.metric("안전", len(df[df["등급"] == "안전"]))
col3.metric("주의", len(df[df["등급"] == "주의"]))
col4.metric("위험", len(df[df["등급"] == "위험"]))

# 지도 생성
map_center = [37.55, 126.99]

m = folium.Map(
    location=map_center,
    zoom_start=11
)

for _, row in filtered_df.iterrows():

    color_map = {
        "안전": "green",
        "주의": "orange",
        "위험": "red"
    }

    folium.Marker(
        location=[row["위도"], row["경도"]],
        popup=f"""
        <b>{row['지역']}</b><br>
        위험도: {row['등급']}<br>
        설명: {row['설명']}
        """,
        tooltip=row["지역"],
        icon=folium.Icon(
            color=color_map.get(row["등급"], "blue")
        )
    ).add_to(m)

st.subheader("📍 안전 지도")

try:
    st_folium(
        m,
        width=None,
        height=500
    )
except Exception as e:
    st.error(f"지도 표시 오류: {e}")

st.subheader("📊 지역 데이터")

st.dataframe(
    filtered_df,
    use_container_width=True
)

csv = filtered_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "📥 CSV 다운로드",
    data=csv,
    file_name="safety_map_data.csv",
    mime="text/csv"
)

st.info(
    "예제 데이터 기반 데모 앱입니다. 실제 공공데이터로 교체하여 활용할 수 있습니다."
)
