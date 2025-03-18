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

    def store_answer(self, question_ids: list, answers: list):
        """
        Supabase의 answers 테이블에 각 질문에 대한 답변을 개별 레코드로 저장
        """
        answer_records = [
            {
                "question_id": question_id,
                "answer": str(answer)
            } for question_id, answer in zip(question_ids, answers)
        ]
        
        response = (
            self.supabase.table("answers")
            .insert(answer_records)
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
        
        # 뉴스 검색 결과 추출
        perplexity_results = response['data']['outputs']["perplexity_results"]
        perplexity_queries = response['data']['outputs']["perplexity_queries"]
        
        tavily_results = response['data']['outputs']["tavily_results"]
        tavily_queries = response['data']['outputs']["tavily_queries"]
    
        queries = perplexity_queries + tavily_queries
        question_ids = self.store_questions(news_id, queries)
        
        urls = []
        
        perplexity_answers = [i["content"] for i in perplexity_results]
        
        for perplexity_result in perplexity_results:
            urls.extend(perplexity_result["citations"])
        
        tavily_answers = [i["results"][0]["raw_content"] for i in tavily_results]
        tavily_urls = [i["results"][0]["url"] for i in tavily_results]
        
        answers = perplexity_answers + tavily_answers
        answer_ids = self.store_answer(question_ids, answers)
        
        urls = urls + tavily_urls
        
        query_answer_list = []  
        for query, answer in zip(queries, answers):
            query_answer_list.append({
                "query": query,
                "answer": answer
            })
        # 생성된 질문들을 news_id와 함께 반환
        return {
            "introduction": introduction,
            "title": title,
            "news_id": news_id,
            "question_ids": question_ids,
            "questions": queries,
            "urls": urls,
            "answers": answers
        }