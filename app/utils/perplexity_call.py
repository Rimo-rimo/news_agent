import asyncio
import aiohttp
import os
import dotenv
from typing import List, Dict, Any

dotenv.load_dotenv()

class PerplexityCall:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.api_url = os.getenv("PERPLEXITY_API_URL")
    
    async def _async_call(self,
                         session: aiohttp.ClientSession,
                         query: str,
                         model: str = "sonar",
                         temperature: float = 0.2,
                         max_tokens: int = 10000,
                         search_recency_days: str = "week") -> Dict[str, Any]:
        """단일 Perplexity API 비동기 호출 메서드"""
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "질문에 대해서 최대한 자세하고 구체적으로 답변해 주세요. 한국어로 답변해 주세요."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": search_recency_days,
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1,
            "web_search_options": {"search_context_size": "high"}
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with session.post(self.api_url, json=payload, headers=headers) as response:
                return await response.json()
        except Exception as e:
            print(f"API 호출 중 오류 발생: {e}")
            return None

    async def parallel_calls(self,
                           queries: List[str],
                           model: str = "sonar",
                           temperature: float = 0.2,
                           max_tokens: int = 10000,
                           search_recency_days: str = "week") -> List[Dict[str, Any]]:
        """여러 쿼리를 병렬로 처리하는 메서드"""

        async with aiohttp.ClientSession() as session:
            tasks = [
                self._async_call(
                    session=session,
                    query=query,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    search_recency_days=search_recency_days
                )
                for query in queries
            ]
            return await asyncio.gather(*tasks)

    def run_parallel_queries(self,
                           queries: List[str],
                           model: str = "sonar",
                           temperature: float = 0.2,
                           max_tokens: int = 10000,
                           search_recency_days: str = "week") -> List[Dict[str, Any]]:
        """병렬 쿼리 실행을 위한 메서드"""
        return asyncio.run(
            self.parallel_calls(
                queries=queries,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                search_recency_days=search_recency_days
            )
        )
