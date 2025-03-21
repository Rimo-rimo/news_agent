from app.config import config
import requests
import dotenv
import os
from supabase import create_client, Client
dotenv.load_dotenv()

class SearchAgent:
    def __init__(self):
        self.url = config.DIFY_WORKFLOW_API_URL
        self.headers = {
            'Authorization': f'Bearer {config.SEARCH_AGENT_API_KEY}',
            'Content-Type': 'application/json'
        }
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
    def store_perplexity_answers(self, question_ids: list, answers: list, urls_list: list):
        """
        Supabase의 perplexity_answers 테이블에 각 질문에 대한 답변을 개별 레코드로 저장
        """
        answer_records = [
            {
                "question_id": question_id,
                "answer": str(answer) if answer else "null",
                "urls": str(urls)
            } for question_id, answer, urls in zip(question_ids, answers, urls_list)
        ]
        
        response = (
            self.supabase.table("perplexity_answers")
            .insert(answer_records)
            .execute()
        )
        
        return [record["id"] for record in response.data]
    
    def store_tavily_answers(self, question_ids: list, answers: list, urls_list: list):
        """
        Supabase의 tavily_answers 테이블에 각 질문에 대한 답변을 개별 레코드로 저장
        """
        answer_records = [
            {
                "question_id": question_id,
                "answer": str(answer) if answer else "null",
                "urls": str(urls)
            } for question_id, answer, urls in zip(question_ids, answers, urls_list)
        ]
        
        response = (
            self.supabase.table("tavily_answers")
            .insert(answer_records)
            .execute()
        )
        
        return [record["id"] for record in response.data]
    

    def run(self, user_id: int, perplexity_questions: list, tavily_questions: list, perplexity_question_ids: list, tavily_question_ids: list):
        payload = {
            'inputs': {
                'perplexity_questions': str(perplexity_questions),
                'tavily_questions': str(tavily_questions)
            },
            'user': str(user_id)
        }
        
        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=230)
        except requests.exceptions.Timeout:
            # 타임아웃 발생 시 처리할 로직
            raise Exception(f"요청 시간이 초과되었습니다. 다시 시도해주세요.")
        
        if response.status_code == 200:
            response_json = response.json()
            perplexity_result = response_json['data']['outputs']["perplexity_result"]
            tavily_result = response_json['data']['outputs']["tavily_result"]
            
            perplexity_answers = [result['content'] for result in perplexity_result]
            perplexity_urls = []
            for result in perplexity_result:
                for url in result['citations']:
                    perplexity_urls.append(url)
            
            tavily_answers = [result["results"][0]['raw_content'] for result in tavily_result]
            tavily_urls = []
            for result in tavily_result:
                tavily_urls.append(result["results"][0]['url'])
                    
            tavily_images = []
            for result in tavily_result:
                for image in result['images']:
                    tavily_images.append(image)
            
            perplexity_answer_ids = self.store_perplexity_answers(perplexity_question_ids, perplexity_answers, perplexity_urls)
            tavily_answer_ids = self.store_tavily_answers(tavily_question_ids, tavily_answers, tavily_urls)
            # return perplexity_answers, tavily_answers
            return {
                "perplexity_answer_ids": perplexity_answer_ids,
                "tavily_answer_ids": tavily_answer_ids,
                "perplexity_answers": perplexity_answers,
                "tavily_answers": tavily_answers,
                "perplexity_urls": perplexity_urls,
                "tavily_urls": tavily_urls,
                "tavily_images": tavily_images,
                "urls": perplexity_urls + tavily_urls
            }
        
        else:
            raise Exception(f"API 호출 실패: {response.status_code}")
