# database.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "coaching_logs.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 딕셔너리처럼 접근 가능
    return conn


def init_db():
    """앱 시작 시 1회 실행. 테이블이 없으면 생성."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS coaching_logs (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                manager_id          TEXT    NOT NULL,
                employee_id         TEXT    NOT NULL,
                coachee_name        TEXT,
                session_date        DATE    NOT NULL,
                conversation_type   TEXT    DEFAULT '코치',
                situation_goal      TEXT,
                observation         TEXT,
                feedback            TEXT,
                agreed_action       TEXT,
                followup_date       DATE,
                raw_input           TEXT,
                generated_log       TEXT,
                created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS coaching_reports (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                manager_id          TEXT    NOT NULL,
                employee_id         TEXT    NOT NULL,
                coachee_name        TEXT,
                department          TEXT,
                role                TEXT,
                period              TEXT,
                metrics_delta       TEXT,
                feedback            TEXT,
                wellbeing           TEXT,
                intuition           TEXT,
                target_fyi          TEXT,
                prompt_version      TEXT,
                generated_report    TEXT,
                created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_report(
    manager_id: str,
    employee_id: str,
    coachee_name: str,
    department: str,
    role: str,
    period: str,
    metrics_delta: str,
    feedback: str,
    wellbeing: str,
    intuition: str,
    target_fyi: str,
    prompt_version: str,
    generated_report: str,
) -> int:
    """코칭 리포트 1건 저장. 저장된 row id 반환."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO coaching_reports (
                manager_id, employee_id, coachee_name,
                department, role, period,
                metrics_delta, feedback, wellbeing, intuition,
                target_fyi, prompt_version, generated_report
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                manager_id, employee_id, coachee_name,
                department, role, period,
                metrics_delta, feedback, wellbeing, intuition,
                target_fyi, prompt_version, generated_report,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_reports_by_employee(manager_id: str, employee_id: str) -> list[dict]:
    """팀원별 코칭 리포트 히스토리 조회."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, coachee_name, department, role,
                   period, target_fyi, prompt_version,
                   generated_report, created_at
            FROM coaching_reports
            WHERE manager_id = ? AND employee_id = ?
            ORDER BY created_at DESC
            """,
            (manager_id, employee_id),
        ).fetchall()
        return [dict(row) for row in rows]


def save_log(
    manager_id: str,
    employee_id: str,
    coachee_name: str,
    session_date: str,
    conversation_type: str,
    situation_goal: str,
    observation: str,
    feedback: str,
    agreed_action: str,
    followup_date: str,
    raw_input: str,
    generated_log: str,
) -> int:
    """코칭 로그 1건 저장. 저장된 row id 반환."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO coaching_logs (
                manager_id, employee_id, coachee_name, session_date,
                conversation_type, situation_goal, observation, feedback,
                agreed_action, followup_date, raw_input, generated_log
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                manager_id, employee_id, coachee_name, session_date,
                conversation_type, situation_goal, observation, feedback,
                agreed_action, followup_date, raw_input, generated_log,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_recent_logs(manager_id: str, employee_id: str, n: int = 2) -> list[dict]:
    """
    Option A 톤 학습용.
    특정 매니저 × 팀원의 최근 n개 로그를 반환.
    manager_id만 넘기면 해당 매니저의 전체 최근 로그 반환.
    """
    with get_connection() as conn:
        if employee_id:
            rows = conn.execute(
                """
                SELECT generated_log, session_date, coachee_name
                FROM coaching_logs
                WHERE manager_id = ? AND employee_id = ?
                ORDER BY session_date DESC, created_at DESC
                LIMIT ?
                """,
                (manager_id, employee_id, n),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT generated_log, session_date, coachee_name
                FROM coaching_logs
                WHERE manager_id = ?
                ORDER BY session_date DESC, created_at DESC
                LIMIT ?
                """,
                (manager_id, n),
            ).fetchall()
        return [dict(row) for row in rows]


def get_today_followups(today: str) -> list[dict]:
    """
    앱 실행 시 배너용. 오늘 팔로업 날짜인 로그 목록 반환.
    MVP 이후 기능 — 지금은 데이터만 준비.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT manager_id, employee_id, coachee_name,
                   agreed_action, followup_date, session_date
            FROM coaching_logs
            WHERE followup_date = ?
            ORDER BY created_at DESC
            """,
            (today,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_logs_by_employee(manager_id: str, employee_id: str) -> list[dict]:
    """팀원별 전체 코칭 히스토리 조회."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, session_date, conversation_type,
                   situation_goal, agreed_action, followup_date, generated_log
            FROM coaching_logs
            WHERE manager_id = ? AND employee_id = ?
            ORDER BY session_date DESC
            """,
            (manager_id, employee_id),
        ).fetchall()
        return [dict(row) for row in rows]