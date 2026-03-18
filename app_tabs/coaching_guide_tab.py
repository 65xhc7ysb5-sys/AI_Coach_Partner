# tabs/coaching_guide_tab.py
# 코칭 가이드 생성 탭
# from tabs import render_coaching_guide_tab 으로 호출

import json
import streamlit as st
from data_models import METRICS, FYI_LIST, ROLE_RECOMMENDED_KEYWORDS
from ai_engine import generate_coaching_report
from database import save_report, get_reports_by_employee
from prompts import LATEST_VERSION


def render_coaching_guide_tab(
    emp_id: str,
    employee_id: str,
    coachee_name: str,
    department: str,
    role: str,
    api_key: str,
    period: str = "QTD",
    selected_version: str = LATEST_VERSION,
):
    """코칭 가이드 생성 탭 전체 렌더링."""

    # ── 1. 성과 데이터 입력 ──
    st.header("1. 성과 데이터 (Dynamic Benchmark 대비 Δ)")
    metrics_list = METRICS[department]
    cols = st.columns(3)
    input_data = {}
    for i, metric in enumerate(metrics_list):
        with cols[i % 3]:
            input_data[metric] = st.text_input(
                f"{metric} Δ", key=f"guide_metric_{metric}"
            )

    st.divider()

    # ── 2. 매니저의 직관 및 맥락 ──
    st.header("2. 매니저의 직관 및 관찰 (Context)")
    col_fb, col_wb, col_in = st.columns(3)
    with col_fb:
        feedback = st.text_area("💬 고객/팀원 피드백", height=150, key="guide_feedback")
    with col_wb:
        wellbeing = st.text_area("🧘 웰빙 상태", height=150, key="guide_wellbeing")
    with col_in:
        intuition = st.text_area("🌟 리더의 직관/관찰", height=150, key="guide_intuition")

    st.divider()

    # ── 3. FYI 역량 선택 ──
    st.header("3. 코칭 가이드 생성")

    recommended = ROLE_RECOMMENDED_KEYWORDS.get(department, {}).get(role, [])
    if recommended:
        st.info(f"💡 **{department} | {role}** 권장 역량: {', '.join(recommended)}")
    else:
        st.info(f"💡 **{department} | {role}**에 대한 권장 역량이 아직 설정되지 않았습니다.")

    default_selection = [
        fyi for fyi in FYI_LIST
        if any(rec in fyi for rec in recommended)
    ]
    selected_fyi = st.multiselect(
        "코칭 집중 역량을 선택하세요 (전체 리스트)",
        FYI_LIST,
        default=default_selection,
        key="guide_fyi",
    )

    # ── 4. 리포트 생성 ──
    if st.button("🚀 코치 페르소나 리포트 생성", type="primary"):
        if not api_key:
            st.error("🚨 .env 파일에 API 키가 없습니다.")
            return

        with st.spinner("전문 코칭 아키텍트가 분석 중입니다..."):
            payload = {
                "Dept": department,
                "Role": role,
                "Metrics_Delta": input_data,
                "Feedback": feedback,
                "Wellbeing": wellbeing,
                "Intuition": intuition,
                "Target_FYI": selected_fyi,
            }
            full_text = generate_coaching_report(
                api_key, payload, version=selected_version
            )

        def parse_result(text: str) -> dict:
            parts = text.split("[")
            res = {}
            for p in parts:
                if "]" in p:
                    tag, content = p.split("]", 1)
                    res[tag.strip()] = content.strip()
            return res

        data = parse_result(full_text)

        # ── 결과 출력 ──
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

        with st.expander("📝 AI 원본 답변 확인 (문제가 생기면 여기를 보세요)"):
            st.code(full_text)

        # ── DB 저장 ──
        if employee_id:
            save_report(
                manager_id=emp_id,
                employee_id=employee_id,
                coachee_name=coachee_name,
                department=department,
                role=role,
                period=period,
                metrics_delta=json.dumps(input_data, ensure_ascii=False),
                feedback=feedback,
                wellbeing=wellbeing,
                intuition=intuition,
                target_fyi=json.dumps(selected_fyi, ensure_ascii=False),
                prompt_version=selected_version,
                generated_report=full_text,
            )
            st.toast(
                f"{coachee_name or employee_id} 코칭 리포트가 저장되었습니다.",
                icon="💾",
            )
        else:
            st.caption("💡 사이드바에서 팀원 사번을 입력하면 리포트가 자동 저장됩니다.")

    st.divider()

    # ── 5. 팀원별 리포트 히스토리 ──
    st.subheader("🗂️ 팀원별 리포트 히스토리")
    lookup_id = st.text_input(
        "조회할 팀원 사번 / 이니셜",
        key="report_history_lookup",
        placeholder="사번 또는 이니셜 입력 후 엔터",
    )
    if lookup_id:
        history = get_reports_by_employee(
            manager_id=emp_id,
            employee_id=lookup_id,
        )
        if not history:
            st.info("해당 팀원의 리포트 기록이 아직 없습니다.")
        else:
            for r in history:
                fyi_list = json.loads(r["target_fyi"]) if r["target_fyi"] else []
                label = (
                    f"{r['created_at'][:10]} | "
                    f"{r['department']} {r['role']} | "
                    f"{r['period']} | "
                    f"v{r['prompt_version']}"
                )
                with st.expander(label):
                    if fyi_list:
                        st.caption(f"FYI 역량: {', '.join(fyi_list)}")
                    st.code(r["generated_report"])