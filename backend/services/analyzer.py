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

        **분석 가이드라인 (중요)**:
        키워드를 다음 3가지 유형 중 하나로 판단하여 분석해:

        1. **🔥 바이럴 트렌드 (Viral Trend) & 파생 유행**:
           - 최근 뉴스, 밈, 방송, SNS 등에서 화제가 되어 급상승한 경우.
           - **[중요] 식재료/부속품일 경우**: 이 재료가 들어가는 **상위 유행(Parent Trend)**이 있는지 반드시 확인해.
             - 예: '피스타치오 스프레드', '카다이프' -> '두바이 초콜릿'의 핵심 재료라서 유행함. (단독 유행 아님)
             - 예: '그릭요거트' -> '요거트 아이스크림(요아정)' 토핑으로 유행함.
           - 분석: "OOO의 핵심 재료/부속품으로 주목받고 있습니다"라고 인과관계를 명확히 설명.

        2. **🍂 계절/날씨 필수가 (Seasonal Necessity)**:
           - 특별한 뉴스 없이, 날씨나 시즌(명절, 휴가철) 때문에 찾는 경우.
           - 분석: 현재 시기(계절)와의 연관성을 설명.

        3. **🛒 생필품/스테디셀러 (Steady Seller)**:
           - 유행과 상관없이 항상 수요가 꾸준한 생필품이나 식재료.
           - 분석: "일상적으로 꾸준히 소비되는 필수품입니다"라고 설명.

        **할루시네이션 방지**:
        - '두바이 쫀득쿠키' -> 두바이산이 아니라 '한국 카페에서 유행하는 디저트'일 수 있음. 한국 웹(나무위키, 블로그) 위주로 검색해.
        
        **응답 스타일 (매우 중요)**:
        - **볼드체(**)**, **[링크]** 등 모든 서식을 사용하지 마.** (순수한 줄글 텍스트만)
        - "분석 결과: ..." 같은 서두 없이 바로 본론만 작성해.
        - **[수치 언급 금지]**: "100을 기록했다", "ratio 90" 같은 구체적인 숫자는 절대 언급하지 마. 대신 "급증했다", "꾸준히 높은 인기를 유지하고 있다", "다소 감소했다" 같은 **정성적인 표현**을 사용해.
        - 제공된 '네이버 검색량 추이' 데이터를 참고하여 추세(Trend)를 설명해.
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

