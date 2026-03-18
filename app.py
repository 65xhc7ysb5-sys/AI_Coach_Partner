# app.py
import os
import streamlit as st
from dotenv import load_dotenv

from database import init_db
from data_models import ROLES
from prompts import AVAILABLE_VERSIONS, LATEST_VERSION
from app_tabs import render_coaching_guide_tab, render_coaching_log_tab

# ── 환경 변수 ──
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ── 매니저 식별자 ──
# TODO: auth 로직 구현 후 로그인 세션에서 자동 주입으로 교체
# 배포 전 단계에서는 .env에 MANAGER_ID를 추가하는 방식으로 확장 가능
MANAGER_ID = os.getenv("MANAGER_ID", "jason")

# ── DB 초기화 (앱 시작 시 1회) ──
init_db()

# ── 페이지 설정 ──
st.set_page_config(page_title="AI Coach Partner", page_icon="🎯", layout="wide")

# ── UI: Expander 높이 통일 ──
st.markdown("""
    <style>
    div[data-testid="stExpander"] div[role="region"] > div {
        height: 280px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# ── 사이드바 ──
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    selected_version = st.selectbox(
        "프롬프트 버전",
        AVAILABLE_VERSIONS,
        index=AVAILABLE_VERSIONS.index(LATEST_VERSION),
    )

    st.header("📋 팀원 기본 정보")
    coachee_name  = st.text_input("팀원 이름")
    employee_id   = st.text_input("팀원 사번 / 이니셜")
    department    = st.selectbox("부서 선택", ["Sales", "Technical Support"])

    _roles        = ROLES[department]
    _role_default = next(
        (i for i, r in enumerate(_roles) if "S2" in r and "FT" in r), 0
    )
    role   = st.selectbox("직급 선택", _roles, index=_role_default)
    period = st.radio("성과 기간", ["WTD", "MTD", "QTD"], index=2)

# ── 타이틀 ──
st.title("🎯 AI Coach Partner")
st.markdown("데이터와 직관을 결합한 예술적 코칭 파트너 (V1.3 MVP)")

# ── 탭 ──
tab1, tab2 = st.tabs(["🎯 코칭 가이드", "📝 코칭 로그"])

with tab1:
    render_coaching_guide_tab(
        emp_id=MANAGER_ID,
        employee_id=employee_id,
        coachee_name=coachee_name,
        department=department,
        role=role,
        api_key=GEMINI_API_KEY,
        period=period,
        selected_version=selected_version,
    )

with tab2:
    render_coaching_log_tab(
        manager_id=MANAGER_ID,
        api_key=GEMINI_API_KEY,
        coachee_id_default=employee_id,
    )