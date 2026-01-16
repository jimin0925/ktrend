import os
import asyncio
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from backend.database import Database

# Load env to get OPENAI_API_KEY
load_dotenv()

class TrendAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            print("[WARNING] No OPENAI_API_KEY found. Analyzer will return mock data.")
            
        # Database
        self.db = Database()

    async def analyze_trend(self, keyword: str):
        """
        Analyze trend using OpenAI's Native Web Search (Implicit) + Naver Datalab Data.
        Returns:
            dict: { "keyword": str, "reason": str, "chart_data": list }
        """
        if not self.client:
            return self._get_mock_analysis(keyword)

        # 1. Fetch Naver Datalab Data (Async wrap)
        from backend.services.naver_datalab import NaverDataLab
        try:
            datalab_service = NaverDataLab()
            chart_data = await asyncio.to_thread(datalab_service.get_daily_trend, keyword, days=365)
            
            # Create a summary for LLM context
            if chart_data:
                peak = max(chart_data, key=lambda x: x['ratio'])
                recent = chart_data[-1] if chart_data else None
                data_context = f"네이버 검색량 추이 (1년): {chart_data[0]['date']}~{chart_data[-1]['date']}. 최고점: {peak['date']} ({peak['ratio']}). 최근: {recent['date']} ({recent['ratio']})."
            else:
                data_context = "네이버 검색량 데이터 없음."
        except Exception as e:
            print(f"Naver DataLab Error: {e}")
            chart_data = []
            data_context = "네이버 검색량 데이터 조회 실패."

        # 2. Check Database for Cached Reason
        cached_analysis = self.db.get_analysis(keyword)
        if cached_analysis:
            print(f"[DB HIT] Returning stored analysis for '{keyword}'")
            return {
                "keyword": keyword,
                "reason": cached_analysis["reason"],
                "chart_data": chart_data # Always return fresh chart data + cached reason
            }

        print(f"Analyzing trend for: {keyword} (LLM Call)...")
        
        # 3. LLM Analysis
        system_prompt = """
        너는 한국의 최신 트렌드를 심층 분석하는 전문가야.
        **웹 검색 기능**을 사용하여 이 키워드가 **왜** 유행하는지 정확한 '유래'와 '이유'를 찾아내.

        **분석 가이드라인**:
        특정한 카테고리에 얽매이지 말고, **현재 시점**에서 검색량이 증가한 **실질적인 핵심 원인**을 분석해.
        다음과 같은 다양한 가능성을 열어두고 생각할 것:

        - **🔥 화제성 (Viral)**: 방송, 유튜브, 밈, SNS 등에서 시작된 유행. (예: 두바이 초콜릿)
        - **💸 경제/사회 (Economic)**: 물가 상승, 할인 행사, 특정 브랜드 세일. (예: 쌀, 생필품)
        - **🍂 계절/날씨 (Seasonal)**: 날씨 변화, 명절, 시즌 이슈. (예: 롱패딩, 선물세트)
        - **🍽 식문화 (Food)**: 새로운 레시피 유행, 제철 음식.

        **[중요] 맥락 파악**:
        - 단순히 "생필품이다"라고 끝내지 말고, "최근 햅쌀 출하시기라서" 혹은 "물가 상승으로 인한 가성비 구매 증가" 처럼 **구체적인 맥락**을 찾아서 설명해.
        - **재료/부속품**일 경우, 이것이 들어가는 **상위 유행(Parent Trend)**이 무엇인지 확인하고 언급해. (예: 피스타치오 -> 두바이 초콜릿 재료)

        **할루시네이션 및 링크 방지**:
        - **과거 이슈 배제**: 키워드가 생필품이거나 일반 명사일 경우, 오래된 연예인 이슈(다이어트 등)를 유행 이유로 들지 마. **현재(최근 1개월)**의 이슈에 집중해.
        - **절대 링크를 포함하지 마.** (http, www, .com 등 금지)
        - 출처 표기 금지: "(news.nate.com)", "[네이버 뉴스]" 같은 텍스트 절대 쓰지 마.
        
        **응답 스타일 (매우 중요)**:
        - **볼드체(**)**, **[링크]** 등 모든 서식을 사용하지 마.** (순수한 줄글 텍스트만)
        - "분석 결과: ..." 같은 서두 없이 바로 본론만 작성해.
        - **[수치 언급 금지]**: "100을 기록했다", "ratio 90" 금지. "급증했다", "높은 인기를 유지하고 있다" 표현 사용.
        """

        user_prompt = f"""
        키워드: '{keyword}'의 정확한 한국 내 유행 이유와 유래를 웹 검색을 통해 분석해줘.
        
        [참고 데이터]
        {data_context}
        """
        
        try:
            # Native Web Search - Implicit (JSON mode not supported with search)
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini-search-preview", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            content = response.choices[0].message.content
            
            # Post-processing: Remove Markdown formatting (links, bold)
            import re
            # Remove links [text](url) -> text
            content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
            # Remove bare URLs
            content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
            # Remove domain citations like (news.nate.com) or (www.naver.com)
            content = re.sub(r'\([a-zA-Z0-9.-]+\.[a-z]{2,}\)', '', content)
            # Remove bold **text** -> text
            content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
            # Remove bold __text__ -> text
            content = re.sub(r'__([^_]+)__', r'\1', content)
            
            # Save to DB
            self.db.save_analysis(keyword, content, chart_data)
            
            return {
                "keyword": keyword,
                "reason": content,
                "chart_data": chart_data
            }
            
        except Exception as e:
            print(f"LLM/Search error: {e}")
            return self._get_mock_analysis(keyword)

    def _get_mock_analysis(self, keyword):
        return {
            "keyword": keyword,
            "reason": "AI 분석 서비스를 사용할 수 없어 임시 데이터를 반환합니다.",
            "chart_data": []
        }

