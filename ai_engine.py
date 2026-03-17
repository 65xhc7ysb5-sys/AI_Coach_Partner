# ai_engine.py
from google import genai
from google.genai import types
from prompts import COACHING_PROMPTS, SYSTEM_MESSAGES, LATEST_VERSION


# Coaching report system

def generate_coaching_report(api_key, payload_data, version, gemini_model='gemini-2.5-flash'):

    try:
        # 1. 최신 Client 초기화
        client = genai.Client(api_key=api_key)

        # 2. 프롬프트 안전하게 가져오기 (KeyError 방지)
        # 요청한 버전이 없으면 LATEST_VERSION으로 자동 대체 (Fallback)
        if version not in COACHING_PROMPTS:
            version = LATEST_VERSION

        base_prompt = COACHING_PROMPTS.get(version)        

        # 3. 데이터 조립
        final_prompt = f"""

            {base_prompt}

            ### [입력 데이터 패키지]
            - 부서/직급: {payload_data.get('Dept')} / {payload_data.get('Role')}
            - 성과(Δ): {payload_data.get('Metrics_Delta')}
            - 고객/팀원 피드백: {payload_data.get('Feedback')}
            - 웰빙 상태: {payload_data.get('Wellbeing')}
            - 리더의 직관/관찰: {payload_data.get('Intuition')}
            - 타겟 FYI 역량: {payload_data.get('Target_FYI')}
            """

        # 4. 최신 SDK 방식으로 콘텐츠 생성
        response = client.models.generate_content(
            model=gemini_model,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_MESSAGES["default"],
                temperature=0.7, # 창의성 조절
            ),
            contents=final_prompt
        )
        
        return response.text

    except Exception as e:
        # 상세한 에러 메시지 출력
        return f"🚨 AI 엔진 오류: {str(e)}"



# Logging system

LOG_SYSTEM_PROMPT = """
당신은 리테일 현장 매니저의 코칭 기록을 정제하는 전문 에디터입니다.

[역할]
매니저가 입력한 코칭 내용을 받아, 아래 원칙을 지키며 코칭 로그를 작성합니다.

[작성 원칙]
1. 톤 유지: 매니저의 관점과 언어를 유지하되, 구어체는 자연스럽게 정제합니다.
   기계적이고 정형화된 문장은 피하세요. 개인화된 대화 톤이 느껴져야 합니다.
2. STAR 구조: Situation → Task/Goal → Action/Observation → Result/Agreed Action
   순서로 흐르도록 재구성합니다. 단, 구조 레이블(S:/T:/A:/R:)은 출력하지 마세요.
3. FYI 역량 키워드: 아래 역량명이 문맥에 자연스럽게 등장하면 **bold** 처리합니다.
   - Customer Focus, Drives Results, Action Oriented, Communicates Effectively,
     Nimble Learning, Self-Development, Strategic Mindset, Courage,
     Interpersonal Savvy, Valuing Differences, Manages Ambiguity, Manages Complexity
4. 역할 기대치 언어: 팀원의 직급과 역할에 맞는 표현을 자연스럽게 사용합니다.
   (예: S1/S2 → "고객 접점에서의 행동", S3/S4 → "팀 기여, 전략적 사고")
5. 합의 액션 + 팔로업: 반드시 본문과 분리하여 마지막에 별도 섹션으로 출력합니다.

[출력 형식]
--- 코칭 로그 본문 ---
(STAR 흐름의 자연스러운 서술. 3-5 문단.)

--- 합의된 액션 ---
(팀원 관점에서 구체적 행동 항목. 번호 리스트.)

--- 다음 팔로업 ---
날짜: {followup_date}
확인 포인트: (합의 액션 이행 여부를 확인할 핵심 질문 1-2개)
"""


def generate_coaching_log(
    api_key: str,
    manager_id: str,
    input_data: dict,
    recent_logs: list[dict],
    gemini_model: str = "gemini-2.5-flash",
) -> str:
    """
    코칭 세션 완료 후 로그 생성.

    Args:
        api_key: Gemini API 키
        manager_id: 매니저 식별자 (톤 학습 컨텍스트용)
        input_data: {
            coachee_name, session_date, conversation_type,
            situation_goal, observation, feedback,
            agreed_action, followup_date
        }
        recent_logs: DB에서 가져온 최근 2개 로그 (Option A 톤 학습)
        gemini_model: 사용할 Gemini 모델명
    """
    try:
        client = genai.Client(api_key=api_key)

        # Option A: 최근 로그를 프롬프트에 삽입하여 톤 학습
        tone_reference = ""
        if recent_logs:
            examples = "\n\n".join(
                f"[이전 로그 {i+1} — {log.get('session_date', '')} / {log.get('coachee_name', '')}]\n{log.get('generated_log', '')}"
                for i, log in enumerate(recent_logs)
            )
            tone_reference = f"""
### [톤 참고 — 이 매니저의 이전 코칭 로그]
아래 예시들의 문체와 톤을 참고하여 새 로그를 작성하세요.
{examples}

---
"""

        # 입력 데이터 조립
        followup_date = input_data.get("followup_date", "미정")
        final_prompt = f"""
{tone_reference}
### [새 코칭 세션 입력 데이터]
- 팀원 이름: {input_data.get('coachee_name')}
- 대화 날짜: {input_data.get('session_date')}
- 대화 유형: {input_data.get('conversation_type', '코치')}
- 상황 및 목표 (코칭 주제): {input_data.get('situation_goal')}
- 관찰 내용 (팀원 관점): {input_data.get('observation')}
- 코치의 제안 / 피드백: {input_data.get('feedback')}
- 합의된 액션 (팀원 관점): {input_data.get('agreed_action')}
- 다음 팔로업 날짜: {followup_date}

위 내용을 바탕으로 코칭 로그를 작성해주세요.
"""

        response = client.models.generate_content(
            model=gemini_model,
            config=types.GenerateContentConfig(
                system_instruction=LOG_SYSTEM_PROMPT.format(followup_date=followup_date),
                temperature=0.4,  # 로그는 창의성보다 일관성 우선
            ),
            contents=final_prompt,
        )

        return response.text

    except Exception as e:
        return f"🚨 로그 생성 오류: {str(e)}"
