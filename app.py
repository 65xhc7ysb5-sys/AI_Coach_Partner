# app.py
import os
import streamlit as st
from dotenv import load_dotenv
from data_models import ROLES, METRICS, FYI_LIST, ROLE_RECOMMENDED_KEYWORDS
from ai_engine import generate_coaching_report
from prompts import AVAILABLE_VERSIONS, LATEST_VERSION
from database import init_db
from coaching_log_tab import render_coaching_log_tab


# .env 파일에서 환경 변수 불러오기
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# --- UI 개선: Expander 창 크기 동일. 내용이 많으면 흐르도록 설정. ---
st.markdown("""
    <style>
    div[data-testid="stExpander"] div[role="region"] > div {
        height: 280px; 
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 사이드바: 버전 관리 기능 추가 ---
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    selected_version = st.selectbox(
        "프롬프트 버전", 
        AVAILABLE_VERSIONS, 
        index=AVAILABLE_VERSIONS.index(LATEST_VERSION)
    )

# --- FYI 권장 역량 데이터 (직급별 매핑) ---
ROLE_RECOMMENDED_FYI = {
    "S1 (PT)": ["22. Nimble Learning", "34. Self-development", "53. Drives Results", "40. Valuing Differences"],
    "S2 (PT)": ["11. Customer Focus", "53. Drives Results", "1. Action Oriented", "15. Courage"],
    "S3 (FT)": ["11. Customer Focus", "53. Drives Results", "33. Strategic Mindset", "7. Communicates Effectively"],
    "S4 (FT)": ["33. Strategic Mindset", "3. Ambiguity", "8. Complexity", "20. Interpersonal Savvy"]
}

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="AI Coach Partner", page_icon="🎯", layout="wide")
st.title("🎯 AI Coach Partner")
st.markdown("데이터와 직관을 결합한 예술적 코칭 파트너 (V1.3 MVP)")

# --- 사이드바: 기본 정보 입력 ---
st.sidebar.header("📋 팀원 기본 정보")
emp_id = st.sidebar.text_input("사번 또는 이니셜")
department = st.sidebar.selectbox("부서 선택", ["Sales", "Technical Support"])
role = st.sidebar.selectbox("직급 선택", ROLES[department])
period = st.sidebar.radio("성과 기간", ["WTD", "MTD", "QTD"])



# --- Connect to DB ---
init_db() 

tab1, tab2 = st.tabs(["🎯 코칭 가이드", "📝 코칭 로그"])

################################################################
# Tab 1: 코칭 가이드
################################################################
# --- 메인 화면: 1. 성과 데이터 입력 ---
with tab1:
    st.header("1. 성과 데이터 (Dynamic Benchmark 대비 Δ)")
    metrics_list = METRICS[department]
    cols = st.columns(3)
    input_data = {}
    for i, metric in enumerate(metrics_list):
        with cols[i % 3]:
            input_data[metric] = st.text_input(f"{metric} Δ")

    st.divider()

    # --- 메인 화면: 2. 매니저의 직관 및 맥락 (3분할) ---
    st.header("2. 매니저의 직관 및 관찰 (Context)")
    col_fb, col_wb, col_in = st.columns(3)
    with col_fb:
        feedback = st.text_area("💬 고객/팀원 피드백", height=150)
    with col_wb:
        wellbeing = st.text_area("🧘 웰빙 상태", height=150)
    with col_in:
        intuition = st.text_area("🌟 리더의 직관/관찰", height=150)

    st.divider()

    # --- 메인 화면: 3. FYI 역량 선택 (에러 방지를 위해 버튼 위에서 정의) ---
    st.header("3. 코칭 가이드 생성")

    # 중첩 딕셔너리에서 데이터 가져오기
    # department 키로 먼저 찾고, 그 안에서 role 키로 찾습니다.
    # 만약 입력해둔 데이터가 없으면 빈 리스트([])를 반환하여 에러를 방지합니다.
    recommended = ROLE_RECOMMENDED_KEYWORDS.get(department, {}).get(role, [])

    if recommended:
        st.info(f"💡 **{department} | {role}** 권장 역량: {', '.join(recommended)}")
    else:
        # 아직 데이터를 채워넣지 않은 직급을 선택했을 때의 안내 문구
        st.info(f"💡 **{department} | {role}**에 대한 권장 역량이 아직 설정되지 않았습니다.")

    # 권장 역량을 '기본 선택(default)'으로 만들어주는 필터링 로직
    # FYI_LIST 내의 텍스트가 recommended 리스트의 텍스트와 일치하는지 확인합니다.
    default_selection = [
        fyi for fyi in FYI_LIST 
        if any(rec in fyi for rec in recommended)
    ]

    # 드롭다운(멀티셀렉트) 렌더링
    # 여기서 selected_fyi 변수에 최종 선택된 역량들이 저장됩니다.
    selected_fyi = st.multiselect(
        "코칭 집중 역량을 선택하세요 (전체 리스트)", 
        FYI_LIST, 
        default=default_selection
    )

    # --- 리포트 생성 및 UI 렌더링 ---
    if st.button("🚀 코치 페르소나 리포트 생성", type="primary"):
        if not emp_id:
            st.warning("사번이나 이니셜을 먼저 입력해주세요!")
        elif not GEMINI_API_KEY:
            st.error("🚨 .env 파일에 API 키가 없습니다.")
        else:
            with st.spinner("전문 코칭 아키텍트가 분석 중입니다..."):
                payload = {
                    "Dept": department, "Role": role, "Metrics_Delta": input_data,
                    "Feedback": feedback, "Wellbeing": wellbeing, "Intuition": intuition,
                    "Target_FYI": selected_fyi
                }
                
                full_text = generate_coaching_report(GEMINI_API_KEY, payload, version="v1.1")
                
                # 텍스트 파싱 함수
                def parse_result(text):
                    parts = text.split("[")
                    res = {}
                    for p in parts:
                        if "]" in p:
                            tag, content = p.split("]", 1)
                            res[tag.strip()] = content.strip()
                    return res

                data = parse_result(full_text)

                # --- 결과 출력 (Progressive Disclosure UI) ---
                st.subheader("🎯 대화 전략 및 방향 (30초 요약)")
                st.info(data.get("SUMMARY", "분석 결과가 없습니다."))

                st.divider()
                st.subheader("🔍 단계별 상세 코칭 가이드")
                g_col, r_col = st.columns(2)
                o_col, w_col = st.columns(2)

                with g_col:
                    with st.expander("🌱 **G**oal (목표 설정)", expanded=True):
                        st.write(data.get("GOAL", "내용 없음"))
                with r_col:
                    with st.expander("📊 **R**eality (현실 점검)", expanded=True):
                        st.write(data.get("REALITY", "내용 없음"))
                with o_col:
                    with st.expander("💡 **O**ptions (Paradigm Shift 질문)", expanded=True):
                        st.write(data.get("OPTIONS", "내용 없음"))
                with w_col:
                    with st.expander("📝 **W**ay Forward (실행 의지)", expanded=True):
                        st.write(data.get("WAY FORWARD", "내용 없음"))

                with st.expander("🛡️ **Defense Bypass & Action Tips**"):
                    st.warning(data.get("DEFENSE", "내용 없음"))

                # 추가: AI가 실제로 보낸 원본 텍스트 확인 (디버깅용)
                with st.expander("📝 AI 원본 답변 확인 (문제가 생기면 여기를 보세요)"):
                    st.code(full_text)


################################################################
# Tab 2: 코칭 로그
################################################################

with tab2:
    render_coaching_log_tab(manager_id=emp_id, api_key=GEMINI_API_KEY, coachee_id_default=emp_id)
