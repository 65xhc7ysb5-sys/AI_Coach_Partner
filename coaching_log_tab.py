# coaching_log_tab.py

import streamlit as st
from datetime import date, timedelta
from database import save_log, get_recent_logs, get_logs_by_employee, get_today_followups
from ai_engine import generate_coaching_log


CONVERSATION_TYPES = ["코치", "분기 대화", "일대일 대화"]

# Temperature 설명 (UI 표시용)
TEMPERATURE_HELP = """
**로그 문체 창의성 조절**

| 값 | 결과 특성 |
|---|---|
| 0.1 – 0.3 | 입력 내용을 거의 그대로 정리. 일관되고 예측 가능한 문장. |
| **0.4 (기본값)** | **균형점. 매니저 톤을 유지하면서 자연스럽게 정제.** |
| 0.5 – 0.7 | 표현이 풍부해지고 문장 다양성 증가. 가끔 예상치 못한 표현 등장. |
| 0.8 – 1.0 | 창의적이지만 원본 의도에서 벗어날 수 있음. 비추천. |

💡 출력이 너무 딱딱하게 느껴지면 **0.5**로, 너무 자유롭게 느껴지면 **0.3**으로 조정해보세요.
"""


def render_coaching_log_tab(
    manager_id: str,
    api_key: str,
    coachee_id_default: str = "",   # ← 사이드바 emp_id를 여기에 전달
):
    """코칭 로그 탭 전체 렌더링."""

    if not manager_id:
        st.warning("사이드바에서 사번 또는 이니셜을 먼저 입력해주세요.")
        return

    # ── 오늘 팔로업 배너 (MVP 이후 기능 — 데이터는 지금부터 쌓음) ──
    today_str = date.today().isoformat()
    followups = get_today_followups(today_str)
    my_followups = [f for f in followups if f["manager_id"] == manager_id]
    if my_followups:
        st.warning(
            f"📌 오늘 팔로업 예정: "
            + ", ".join(f["coachee_name"] for f in my_followups)
        )

    st.header("📝 코칭 로그 작성")
    st.caption("세션 완료 후 입력 → AI가 STAR 기반 로그로 정제합니다.")

    # ── Temperature 슬라이더 (폼 바깥 — 즉시 반영) ──
    with st.expander("⚙️ 로그 문체 설정", expanded=False):
        temperature = st.slider(
            "문체 창의성 (Temperature)",
            min_value=0.1,
            max_value=1.0,
            value=0.4,
            step=0.1,
            help=TEMPERATURE_HELP,
        )
        st.markdown(TEMPERATURE_HELP)

    # ── 입력 폼 ──
    with st.form("coaching_log_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            coachee_name = st.text_input("팀원 이름 *")
            # 사이드바 emp_id가 있으면 자동 채움, 수동 수정도 가능
            employee_id = st.text_input(
                "팀원 사번 / 이니셜 *",
                value=coachee_id_default,
                help="사이드바의 사번이 자동으로 입력됩니다. 필요 시 수정하세요.",
            )

        with col2:
            session_date = st.date_input("대화 날짜", value=date.today())
            conversation_type = st.selectbox(
                "대화 유형", CONVERSATION_TYPES, index=0
            )

        with col3:
            followup_date = st.date_input(
                "다음 팔로업 날짜",
                value=date.today() + timedelta(days=14),
            )

        st.divider()

        situation_goal = st.text_area(
            "상황 및 목표 (코칭 주제) *",
            height=100,
            placeholder="이번 대화의 주제와 배경을 간략히 적어주세요.",
        )

        col_obs, col_fb = st.columns(2)
        with col_obs:
            observation = st.text_area(
                "관찰 내용 (팀원 관점)",
                height=120,
                placeholder="팀원이 표현한 생각, 감정, 상황 인식",
            )
        with col_fb:
            feedback = st.text_area(
                "코치의 제안 / 피드백",
                height=120,
                placeholder="내가 전달한 피드백 또는 제안한 관점",
            )

        agreed_action = st.text_area(
            "합의된 액션 (팀원 관점) *",
            height=100,
            placeholder="팀원이 다음 세션까지 실행하기로 한 것들",
        )

        submitted = st.form_submit_button("🚀 코칭 로그 생성", type="primary")

    # ── 로그 생성 ──
    if submitted:
        if not coachee_name or not employee_id or not situation_goal or not agreed_action:
            st.error("* 표시 필드를 모두 입력해주세요.")
            return

        if not api_key:
            st.error("🚨 .env 파일에 API 키가 없습니다.")
            return

        with st.spinner("코칭 로그를 정제하는 중입니다..."):
            # Option A: 동일 매니저 × 동일 팀원의 최근 2개 로그 가져오기
            recent_logs = get_recent_logs(
                manager_id=manager_id,
                employee_id=employee_id,
                n=2,
            )

            input_data = {
                "coachee_name": coachee_name,
                "session_date": session_date.isoformat(),
                "conversation_type": conversation_type,
                "situation_goal": situation_goal,
                "observation": observation,
                "feedback": feedback,
                "agreed_action": agreed_action,
                "followup_date": followup_date.isoformat(),
            }

            raw_input_text = str(input_data)

            generated = generate_coaching_log(
                api_key=api_key,
                manager_id=manager_id,
                input_data=input_data,
                recent_logs=recent_logs,
                temperature=temperature,
            )

        # ── 결과 출력 ──
        st.success("✅ 코칭 로그가 생성되었습니다.")
        st.markdown(generated)

        # 복사 편의를 위한 raw 텍스트 영역
        with st.expander("📋 복사용 텍스트 (사내 코칭 도구에 붙여넣기)"):
            st.text_area("", value=generated, height=300, label_visibility="collapsed")

        # DB 저장
        save_log(
            manager_id=manager_id,
            employee_id=employee_id,
            coachee_name=coachee_name,
            session_date=session_date.isoformat(),
            conversation_type=conversation_type,
            situation_goal=situation_goal,
            observation=observation,
            feedback=feedback,
            agreed_action=agreed_action,
            followup_date=followup_date.isoformat(),
            raw_input=raw_input_text,
            generated_log=generated,
        )

        # 저장 확인 토스트
        st.toast(f"{coachee_name}님 코칭 로그가 저장되었습니다.", icon="💾")

    st.divider()

    # ── 팀원별 히스토리 조회 ──
    st.subheader("🗂️ 팀원별 코칭 히스토리")
    lookup_employee_id = st.text_input(
        "조회할 팀원 사번 / 이니셜",
        key="history_lookup",
        placeholder="사번 또는 이니셜 입력 후 엔터",
    )

    if lookup_employee_id:
        history = get_logs_by_employee(
            manager_id=manager_id,
            employee_id=lookup_employee_id,
        )
        if not history:
            st.info("해당 팀원의 코칭 기록이 아직 없습니다.")
        else:
            for log in history:
                label = f"{log['session_date']} | {log['conversation_type']} | 팔로업: {log.get('followup_date', '미정')}"
                with st.expander(label):
                    st.markdown(log["generated_log"])