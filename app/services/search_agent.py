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
        
    def store_answer(self, question_ids: list, answers: list):
        """
        Supabase의 answers 테이블에 각 질문에 대한 답변을 개별 레코드로 저장
        """
        answer_records = [
            {
                "question_id": question_id,
                "answer": answer
            } for question_id, answer in zip(question_ids, answers)
        ]
        
        response = (
            self.supabase.table("answers")
            .insert(answer_records)
            .execute()
        )
        
        return [record["id"] for record in response.data]

    def search_answer(self, user_id: int, questions: str, question_ids: list):
        payload = {
            'inputs': {
                'questions': questions
            },
            'user': str(user_id)
        }
        
        response = requests.post(self.url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            answers = response.json()['data']['outputs']["search_result"]
            answer_ids = self.store_answer(question_ids, answers)
            return answers
        
        else:
            raise Exception(f"API 호출 실패: {response.status_code}")
