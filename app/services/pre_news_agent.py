from app.config import config
import requests
import dotenv
import os
from supabase import create_client, Client
from datetime import datetime
import json

dotenv.load_dotenv()

class PreNewsAgent:
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

    def store_perplexity_questions(self, news_id: int, questions: list):
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
            self.supabase.table("perplexity_questions")
            .insert(question_records)
            .execute()
        )
        
        return [record["id"] for record in response.data]
    
    def store_tavily_questions(self, news_id: int, questions: list):
        """
        Supabase의 tavily_questions 테이블에 각 질문을 개별 레코드로 저장
        """
        question_records = [
            {
                "news_id": news_id,
                "question": question
            } for question in questions
        ]
        
        response = (
            self.supabase.table("tavily_questions")
            .insert(question_records)
            .execute()
        )
        
        return [record["id"] for record in response.data]
    
    def run(self, user_id: int, news_id: int, news_content: str, question_n: int):
        # 뉴스 저장 로직 제거 (이미 crawl_agent에서 저장됨)
        
        payload = {
            'inputs': {
                'news_content': news_content,
                'question_n': question_n
            },
            'user': str(user_id)
        }
        
        response = requests.post(self.url, headers=self.headers, json=payload).json()


        # 제목과 소개 추출
        title_introduction = response['data']['outputs']["title_introduction"]
        try:
            title_introduction = json.loads(title_introduction)
        except:
            title_introduction = title_introduction.replace("\n", " ")
            title_introduction = json.loads(title_introduction)
        title = title_introduction["title"]
        introduction = title_introduction["introduction"]
        
        # query 추출
        perplexity_questions = response['data']['outputs']["perplexity_queries"]
        tavily_questions = response['data']['outputs']["tavily_queries"]
    
        perplexity_question_ids = self.store_perplexity_questions(news_id, perplexity_questions)
        tavily_question_ids = self.store_tavily_questions(news_id, tavily_questions)

        # 생성된 질문들을 news_id와 함께 반환
        return {
            "title": title,
            "introduction": introduction,
            "news_id": news_id,
            "perplexity_question_ids": perplexity_question_ids,
            "tavily_question_ids": tavily_question_ids,
            "perplexity_questions": perplexity_questions,
            "tavily_questions": tavily_questions
        }