# app.py
import streamlit as st
from data_models import ROLES, METRICS, FYI_LIST

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="AI Coach Partner", page_icon="🎯", layout="wide")
st.title("🎯 AI Coach Partner")
st.markdown("데이터와 직관을 결합한 예술적 코칭 파트너")

# --- 사이드바: 기본 정보 입력 ---
st.sidebar.header("📋 팀원 기본 정보")
emp_id = st.sidebar.text_input("사번 또는 이니셜 (마스킹 처리됨)")

department = st.sidebar.selectbox("부서 선택", ["Sales", "Technical Support"])
role = st.sidebar.selectbox("직급 선택", ROLES[department])

period = st.sidebar.radio("성과 기간", ["WTD", "MTD", "QTD"])

# --- 메인 화면: Step 1. 성과 데이터 입력 (동적 렌더링) ---
st.header("1. 성과 데이터 (Dynamic Benchmark 대비 Δ)")
st.caption(f"선택하신 **{department}** 부서의 핵심 지표입니다. 데이터가 없다면 비워두셔도 좋습니다.")

# 선택한 부서의 지표를 불러와서 여러 열(columns)로 나누어 배치
metrics_list = METRICS[department]
cols = st.columns(3) # 3열로 배치

input_data = {}
for i, metric in enumerate(metrics_list):
    col_idx = i % 3
    with cols[col_idx]:
        # 빈칸(None) 허용을 위해 value는 비워둠
        input_data[metric] = st.text_input(f"{metric} Δ")

st.divider()

# --- 메인 화면: Step 2. 리더의 직관 및 맥락 ---
st.header("2. 매니저의 직관 및 관찰 (Context)")
col_feedback, col_intuition = st.columns(2)

with col_feedback:
    feedback = st.text_area("고객 및 동료 피드백 / 웰빙 상태", height=150, placeholder="예: 최근 수면 부족 호소, 제품 설명이 전문적이라는 고객 칭찬...")

with col_intuition:
    intuition = st.text_area("리더의 직관 (Intuition) 🌟", height=150, placeholder="예: 수치는 좋으나 에너지가 고갈된 느낌. 팀워크보다 개인 성과에 매몰된 것 같음...")

st.divider()

# --- 메인 화면: Step 3. 역량 선택 및 리포트 생성 ---
st.header("3. 코칭 가이드 생성")
selected_fyi = st.multiselect("이번 코칭에서 집중할 FYI 역량을 선택하세요 (AI 추천 전 수동 선택)", FYI_LIST, max_selections=3)

if st.button("🚀 코치 페르소나 리포트 생성", type="primary"):
    if not emp_id:
        st.warning("사번이나 이니셜을 먼저 입력해주세요!")
    else:
        st.info("AI 엔진이 JD, FYI 역량, 성과 데이터, 직관을 분석하여 리포트를 작성 중입니다... (다음 단계에서 연결 예정)")
        
        # 입력된 데이터 요약 확인용 출력
        with st.expander("입력된 데이터 페이로드 확인 (디버깅용)"):
            st.json({
                "ID": emp_id,
                "Dept": department,
                "Role": role,
                "Period": period,
                "Metrics_Delta": input_data,
                "Feedback": feedback,
                "Intuition": intuition,
                "Target_FYI": selected_fyi
            })