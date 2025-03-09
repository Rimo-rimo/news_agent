from app.config import config
import requests
import dotenv
import os
from supabase import create_client, Client
from datetime import datetime
import json

dotenv.load_dotenv()

class QuestionGenerator:
    def __init__(self):
        self.url = config.DIFY_WORKFLOW_API_URL
        self.headers = {
            'Authorization': f'Bearer {config.QUESTION_GENERATOR_API_KEY}',
            'Content-Type': 'application/json'
        }
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

    def store_questions(self, news_id: int, questions: list):
        """
        Supabase의 questions 테이블에 각 질문을 개별 레코드로 저장
        """
        question_records = [
            {
                "news_id": news_id,
                "question": question
            } for question in questions
        ]
        
        response = (
            self.supabase.table("questions")
            .insert(question_records)
            .execute()
        )
        
        return [record["id"] for record in response.data]
    
    def generate_questions(self, user_id: int, news_id: int, news_content: str, question_n: int):
        # 뉴스 저장 로직 제거 (이미 crawl_agent에서 저장됨)
        
        payload = {
            'inputs': {
                'news_content': news_content,
                'question_n': question_n
            },
            'user': str(user_id)
        }
        
        response = requests.post(self.url, headers=self.headers, json=payload)

        if response.status_code == 200:
            title_introduction = json.loads(response.json()['data']['outputs']["title_introduction"])
            title = title_introduction["title"]
            introduction = title_introduction["introduction"]
            questions = json.loads(response.json()['data']['outputs']["questions"])["questions"]
            question_ids = self.store_questions(news_id, questions)
            # 생성된 질문들을 news_id와 함께 반환
            return {
                "news_id": news_id,
                "question_ids": question_ids,
                "questions": questions,
                "introduction": introduction,
                "title": title
            }
        else:
            raise Exception(f"API 호출 실패: {response.status_code}")