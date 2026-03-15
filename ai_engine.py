# ai_engine.py
from google import genai
from google.genai import types
from prompts import COACHING_PROMPTS, SYSTEM_MESSAGES, LATEST_VERSION

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