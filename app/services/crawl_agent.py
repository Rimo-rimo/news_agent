from app.config import config
import requests
import dotenv
import os
from supabase import create_client, Client
import json

dotenv.load_dotenv()

class CrawlAgent:
    def __init__(self):
        self.url = config.DIFY_WORKFLOW_API_URL
        self.headers = {
            'Authorization': f'Bearer {config.CRAWL_AGENT_API_KEY}',
            'Content-Type': 'application/json'
        }
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
    
    def store_crawl_result(self, user_id: int, url: str, content: str) -> int:
        """
        Supabase에 크롤링 결과를 저장하고 저장된 데이터의 ID를 반환
        """
        data = {
            "user_id": user_id,
            "url": url,
            "content": content
        }
        
        response = (
            self.supabase.table("news")
            .insert(data)
            .execute()
        )
        
        return response.data[0]["id"]
    
    def run(self, user_id: int, url: str):
        """
        지정된 URL에서 콘텐츠를 크롤링하고 결과를 저장
        """
        payload = {
            'inputs': {
                'url': url
            },
            'user': str(user_id)
        }
        
        response = requests.post(self.url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            content = response.json()['data']['outputs']["content"]
            news_id = self.store_crawl_result(user_id, url, content)
            
            return {
                "news_id": news_id,
                "url": url,
                "content": content
            }
        else:
            raise Exception(f"API 호출 실패: {response.status_code}")
