import asyncio
from tavily import AsyncTavilyClient
import os
import dotenv
from typing import List, Dict, Any

dotenv.load_dotenv()

import nest_asyncio
nest_asyncio.apply()

class TavilyCall:
    def __init__(self):
        self.client = AsyncTavilyClient()
    
    async def _async_call(self, query: str) -> Dict[str, Any]:
        """단일 Tavily API 비동기 호출 메서드"""
        try:
            response = await self.client.search(query=query)
            return response
        except Exception as e:
            print(f"API 호출 중 오류 발생: {e}")
            return None

    async def parallel_calls(self, queries: List[str]) -> List[Dict[str, Any]]:
        """여러 쿼리를 병렬로 처리하는 메서드"""
        tasks = [self._async_call(query) for query in queries]
        return await asyncio.gather(*tasks)

    def run_parallel_queries(self, queries: List[str]) -> List[Dict[str, Any]]:
        """병렬 쿼리 실행을 위한 메서드"""
        return asyncio.run(self.parallel_calls(queries=queries))