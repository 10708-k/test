import streamlit as st
from google import genai

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="안전 귀가 도우미 챗봇",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ 안전 귀가 도우미 챗봇")
st.caption("혼자 귀가하는 사회적 약자를 위한 안전 솔루션 추천 AI")

# -----------------------------
# API 키 확인
# -----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "GEMINI_API_KEY가 설정되지 않았습니다.\n\n"
        "Streamlit Secrets에 API 키를 추가해주세요."
    )
    st.stop()

# Gemini 클라이언트 생성
client = genai.Client(api_key=api_key)

# -----------------------------
# 시스템 프롬프트
# -----------------------------
SYSTEM_PROMPT = """
당신은 '안전 귀가 도우미 AI'입니다.

목적:
혼자 귀가하는 사회적 약자(여성, 아동, 노인, 장애인 등)의
안전 문제를 해결하기 위한 실질적인 방법을 제안합니다.

답변 원칙:
1. 현실적인 안전 수칙을 제시한다.
2. 스마트폰 앱, 위치 공유, 안심 귀가 서비스 등을 추천할 수 있다.
3. 긴급 상황에서는 경찰(112) 또는 응급기관 이용을 안내한다.
4. 위험한 행동을 권장하지 않는다.
5. 답변은 친절하고 이해하기 쉽게 작성한다.
6. 한국 상황을 기준으로 설명한다.
"""

# -----------------------------
# 채팅 기록 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# 사용자 입력
# -----------------------------
user_input = st.chat_input(
    "귀가 안전에 대해 질문해보세요."
)

if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    try:

        # Gemini용 대화 이력 생성
        conversation = SYSTEM_PROMPT + "\n\n"

        for msg in st.session_state.messages:
            role = "사용자" if msg["role"] == "user" else "AI"
            conversation += f"{role}: {msg['content']}\n"

        with st.chat_message("assistant"):

            with st.spinner("답변 생성 중..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=conversation
                )

                answer = response.text

                st.markdown(answer)

        # 답변 저장
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    except Exception as e:

        error_msg = f"""
죄송합니다. 답변 생성 중 오류가 발생했습니다.

오류 내용:
`{str(e)}`
"""

        with st.chat_message("assistant"):
            st.error(error_msg)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_msg
            }
        )

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:

    st.header("📌 예시 질문")

    st.write("""
- 밤길이 무서운데 어떻게 귀가하면 좋을까?
- 여성 안심 귀가 서비스가 있나요?
- 노인이 혼자 귀가할 때 주의사항은?
- 위치 공유 앱 추천해줘.
- 위험 상황이면 어떻게 대처해야 하나요?
""")

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()
