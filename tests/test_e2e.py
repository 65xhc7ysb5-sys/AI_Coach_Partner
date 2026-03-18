# tests/test_e2e.py
# 실행: python -m tests.test_e2e

import sys
import os
import json
import sqlite3
import tempfile
import importlib
from datetime import date, timedelta

# 프로젝트 루트를 Python path에 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# ── 테스트용 임시 DB 경로 주입 ──
# 실제 coaching_logs.db를 건드리지 않음
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
os.environ["COACHING_DB_PATH"] = _tmp_db.name

PASS = "✅"
FAIL = "❌"
results = []


def check(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    results.append((status, name, detail))
    print(f"  {status}  {name}" + (f" — {detail}" if detail else ""))
    return condition


# ══════════════════════════════════════════════
# STEP 1 | Import 검증
# ══════════════════════════════════════════════
print("\n[ STEP 1 ] Import 검증")

try:
    import database
    # DB 경로를 임시 파일로 오버라이드
    database.DB_PATH = _tmp_db.name
    check("database.py import", True)
except Exception as e:
    check("database.py import", False, str(e))

try:
    from database import (
        init_db, save_log, save_report,
        get_recent_logs, get_logs_by_employee,
        get_reports_by_employee, get_today_followups,
    )
    check("database 함수 전체 import", True)
except Exception as e:
    check("database 함수 전체 import", False, str(e))

try:
    from ai_engine import generate_coaching_log
    check("ai_engine.py (generate_coaching_log) import", True)
    _ai_engine_available = True
except ImportError as e:
    err = str(e)
    if any(k in err for k in ("genai", "google", "ai_engine")):
        print(f"  ⚠️   ai_engine.py import — 외부 의존성 미설치, 시그니처 검증 스킵")
        generate_coaching_log = None
        _ai_engine_available = False
    else:
        check("ai_engine.py (generate_coaching_log) import", False, err)
        _ai_engine_available = False
except AttributeError as e:
    # ai_engine.py는 있지만 generate_coaching_log 함수가 없는 경우
    check("ai_engine.py (generate_coaching_log) import", False, str(e))
    _ai_engine_available = False

# app_tabs (배포명) 또는 tabs (개발명) 둘 다 시도
_tabs_available = False
render_coaching_guide_tab = None
render_coaching_log_tab = None
for _pkg in ("app_tabs", "tabs"):
    try:
        _mod = importlib.import_module(_pkg)
        render_coaching_guide_tab = _mod.render_coaching_guide_tab
        render_coaching_log_tab   = _mod.render_coaching_log_tab
        check(f"tabs 패키지 import ({_pkg})", True)
        _tabs_available = True
        break
    except Exception:
        continue
if not _tabs_available:
    print("  ⚠️   tabs 패키지 import — streamlit 의존성으로 인해 스킵")


# ══════════════════════════════════════════════
# STEP 2 | DB 초기화 검증
# ══════════════════════════════════════════════
print("\n[ STEP 2 ] DB 초기화 검증")

try:
    init_db()
    check("init_db() 실행", True)
except Exception as e:
    check("init_db() 실행", False, str(e))

try:
    conn = sqlite3.connect(_tmp_db.name)
    tables = {
        row[0] for row in
        conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    conn.close()
    check("coaching_logs 테이블 존재", "coaching_logs" in tables)
    check("coaching_reports 테이블 존재", "coaching_reports" in tables)
except Exception as e:
    check("테이블 존재 확인", False, str(e))


# ══════════════════════════════════════════════
# STEP 3 | coaching_logs CRUD 검증
# ══════════════════════════════════════════════
print("\n[ STEP 3 ] coaching_logs CRUD 검증")

TEST_MANAGER  = "test_manager"
TEST_EMPLOYEE = "EMP_TEST_001"
TODAY         = date.today().isoformat()
FOLLOWUP      = (date.today() + timedelta(days=14)).isoformat()

try:
    row_id = save_log(
        manager_id=TEST_MANAGER,
        employee_id=TEST_EMPLOYEE,
        coachee_name="테스트 팀원",
        session_date=TODAY,
        conversation_type="코치",
        situation_goal="고객 응대 품질 향상",
        observation="팀원이 주도적으로 개선 의지를 보임",
        feedback="구체적인 행동 변화 3가지를 제안함",
        agreed_action="다음 주까지 고객 피드백 3건 직접 수집",
        followup_date=FOLLOWUP,
        raw_input="테스트 원본 입력",
        generated_log="테스트 생성 로그 내용입니다.",
    )
    check("save_log() 저장", isinstance(row_id, int) and row_id > 0, f"row_id={row_id}")
except Exception as e:
    check("save_log() 저장", False, str(e))

try:
    logs = get_recent_logs(TEST_MANAGER, TEST_EMPLOYEE, n=2)
    check(
        "get_recent_logs() 조회",
        len(logs) == 1 and logs[0]["coachee_name"] == "테스트 팀원",
        f"{len(logs)}건 반환"
    )
except Exception as e:
    check("get_recent_logs() 조회", False, str(e))

try:
    history = get_logs_by_employee(TEST_MANAGER, TEST_EMPLOYEE)
    check(
        "get_logs_by_employee() 조회",
        len(history) >= 1,
        f"{len(history)}건 반환"
    )
except Exception as e:
    check("get_logs_by_employee() 조회", False, str(e))

try:
    followups = get_today_followups(FOLLOWUP)
    check(
        "get_today_followups() 조회",
        any(f["employee_id"] == TEST_EMPLOYEE for f in followups),
        f"{len(followups)}건 반환"
    )
except Exception as e:
    check("get_today_followups() 조회", False, str(e))


# ══════════════════════════════════════════════
# STEP 4 | coaching_reports CRUD 검증
# ══════════════════════════════════════════════
print("\n[ STEP 4 ] coaching_reports CRUD 검증")

try:
    report_id = save_report(
        manager_id=TEST_MANAGER,
        employee_id=TEST_EMPLOYEE,
        coachee_name="테스트 팀원",
        department="Sales",
        role="S2 (FT)",
        period="QTD",
        metrics_delta=json.dumps({"NPS": "+3", "Unit": "+5"}, ensure_ascii=False),
        feedback="고객 피드백 긍정적",
        wellbeing="안정적",
        intuition="성장 의지 높음",
        target_fyi=json.dumps(["11. Customer Focus", "53. Drives Results"], ensure_ascii=False),
        prompt_version="v1.1",
        generated_report="테스트 리포트 내용입니다.",
    )
    check("save_report() 저장", isinstance(report_id, int) and report_id > 0, f"row_id={report_id}")
except Exception as e:
    check("save_report() 저장", False, str(e))

try:
    reports = get_reports_by_employee(TEST_MANAGER, TEST_EMPLOYEE)
    check(
        "get_reports_by_employee() 조회",
        len(reports) >= 1 and reports[0]["department"] == "Sales",
        f"{len(reports)}건 반환"
    )
except Exception as e:
    check("get_reports_by_employee() 조회", False, str(e))


# ══════════════════════════════════════════════
# STEP 5 | 톤 학습 컨텍스트 생성 검증 (Option A)
# ══════════════════════════════════════════════
print("\n[ STEP 5 ] 톤 학습 컨텍스트 (Option A) 검증")

try:
    # 로그를 1건 더 저장해서 n=2 쿼리 검증
    save_log(
        manager_id=TEST_MANAGER,
        employee_id=TEST_EMPLOYEE,
        coachee_name="테스트 팀원",
        session_date=(date.today() - timedelta(days=30)).isoformat(),
        conversation_type="코치",
        situation_goal="이전 세션 주제",
        observation="이전 관찰",
        feedback="이전 피드백",
        agreed_action="이전 합의 액션",
        followup_date=(date.today() - timedelta(days=16)).isoformat(),
        raw_input="이전 원본",
        generated_log="이전 세션 로그 내용입니다.",
    )
    recent = get_recent_logs(TEST_MANAGER, TEST_EMPLOYEE, n=2)
    check(
        "최근 2개 로그 반환 (톤 학습용)",
        len(recent) == 2,
        f"{len(recent)}건 반환"
    )
    check(
        "최신 로그가 첫 번째",
        recent[0]["session_date"] >= recent[1]["session_date"],
        f"{recent[0]['session_date']} ≥ {recent[1]['session_date']}"
    )
except Exception as e:
    check("톤 학습 컨텍스트 검증", False, str(e))


# ══════════════════════════════════════════════
# STEP 6 | generate_coaching_log 시그니처 검증
# ══════════════════════════════════════════════
print("\n[ STEP 6 ] AI 엔진 시그니처 검증")

if not _ai_engine_available:
    print("  ⚠️   google-genai 미설치 — 스킵")
else:
    try:
        import inspect
        sig = inspect.signature(generate_coaching_log)
        params = list(sig.parameters.keys())
        required = ["api_key", "manager_id", "input_data", "recent_logs", "temperature"]
        missing = [p for p in required if p not in params]
        check(
            "generate_coaching_log 파라미터 확인",
            len(missing) == 0,
            f"누락: {missing}" if missing else f"파라미터: {params}"
        )
        default_temp = sig.parameters["temperature"].default
        check(
            "temperature 기본값 0.4",
            default_temp == 0.4,
            f"실제 기본값: {default_temp}"
        )
    except Exception as e:
        check("AI 엔진 시그니처 검증", False, str(e))


# ══════════════════════════════════════════════
# STEP 7 | app_tabs 함수 시그니처 검증
# ══════════════════════════════════════════════
print("\n[ STEP 7 ] app_tabs 함수 시그니처 검증")

if not _tabs_available:
    print("  ⚠️   streamlit 의존성으로 인해 스킵")
else:
    try:
        import inspect
        sig_guide = inspect.signature(render_coaching_guide_tab)
        guide_params = list(sig_guide.parameters.keys())
        required_guide = ["emp_id", "employee_id", "coachee_name", "department", "role", "api_key"]
        missing_guide = [p for p in required_guide if p not in guide_params]
        check(
            "render_coaching_guide_tab 파라미터",
            len(missing_guide) == 0,
            f"누락: {missing_guide}" if missing_guide else "OK"
        )
    except Exception as e:
        check("render_coaching_guide_tab 시그니처", False, str(e))

    try:
        import inspect
        sig_log = inspect.signature(render_coaching_log_tab)
        log_params = list(sig_log.parameters.keys())
        required_log = ["manager_id", "api_key", "coachee_id_default"]
        missing_log = [p for p in required_log if p not in log_params]
        check(
            "render_coaching_log_tab 파라미터",
            len(missing_log) == 0,
            f"누락: {missing_log}" if missing_log else "OK"
        )
    except Exception as e:
        check("render_coaching_log_tab 시그니처", False, str(e))


# ══════════════════════════════════════════════
# 결과 요약
# ══════════════════════════════════════════════
print("\n" + "═" * 50)
print("  검증 결과 요약")
print("═" * 50)

passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)

if failed:
    print(f"\n  {FAIL} 실패 항목:")
    for r in results:
        if r[0] == FAIL:
            print(f"     • {r[1]}" + (f": {r[2]}" if r[2] else ""))

print(f"\n  총 {len(results)}개 항목 — {PASS} {passed}개 통과 / {FAIL} {failed}개 실패\n")

# ── 임시 DB 정리 ──
os.unlink(_tmp_db.name)

# pytest 호환: 실패 항목 있으면 exit code 1
if failed:
    sys.exit(1)