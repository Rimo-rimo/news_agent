from app.config import config
import requests
import dotenv
import os
from supabase import create_client, Client
import urllib.parse
from bs4 import BeautifulSoup
import concurrent.futures
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
    
    def store_citations(self, news_id: int, urls: list, titles: list):
        """
        Supabase의 citations 테이블에 각 질문에 대한 참고 문서 URL을 개별 레코드로 저장
        """
        answer_records = [
            {
                "news_id": news_id,
                "urls": str(urls),
                "titles": str(titles)
            }
        ]
        
        response = (
            self.supabase.table("citations")
            .insert(answer_records)
            .execute()
        )
        
        return [record["id"] for record in response.data]

    def store_image_urls(self, news_id: int, image_urls: list):
        """
        Supabase의 image_urls 테이블에 각 질문에 대한 이미지 URL을 개별 레코드로 저장
        """
        answer_records = [
            {
                "news_id": news_id,
                "urls": str(image_urls)
            }
        ]
        
        response = (
            self.supabase.table("image_urls")
            .insert(answer_records)
            .execute()
        )
        
        return [record["id"] for record in response.data]
        
    def get_page_title(self, url):
        try:
            # 타임아웃을 짧게 설정하여 응답 지연 방지
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 페이지 제목 가져오기
                title = soup.title.string if soup.title else None
                
                # 제목이 너무 길면 자르기
                if title and len(title) > 50:
                    title = title[:36] + "..."
                    
                return title if title else urllib.parse.urlparse(url).netloc
            return urllib.parse.urlparse(url).netloc
        except Exception as e:
            # 오류 발생 시 도메인 이름 반환
            return urllib.parse.urlparse(url).netloc 

    def get_page_titles_parallel(self, urls, max_workers=30):
        """여러 URL의 페이지 제목을 병렬로 가져옵니다."""
        titles = [None] * len(urls)
        favicon_urls = [None] * len(urls)
        
        def process_url(index_url):
            index, url = index_url
            parsed_url = urllib.parse.urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
            title = self.get_page_title(url)
            return index, title, favicon_url
        
        # 병렬로 URL 처리
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # URL과 인덱스를 함께 전달
            results = executor.map(process_url, enumerate(urls))
            
            # 결과 저장
            for index, title, favicon_url in results:
                titles[index] = title
                favicon_urls[index] = favicon_url
                
        return titles, favicon_urls

    def run(self, user_id: int, news_id: int, perplexity_questions: list, tavily_questions: list, perplexity_question_ids: list, tavily_question_ids: list):
        payload = {
            'inputs': {
                'perplexity_questions': str(perplexity_questions),
                'tavily_questions': str(tavily_questions)
            },
            'user': str(user_id)
        }
        
        try:
            response = requests.post(self.url, headers=self.headers, json=payload)
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
                    
            image_url_ids = self.store_image_urls(news_id, tavily_images)
                    
            urls = perplexity_urls + tavily_urls
            titles, favicon_urls = self.get_page_titles_parallel(urls)
            citation_ids = self.store_citations(news_id, urls, titles)
            
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
                "urls": urls,
                "url_titles": titles,
                "favicon_urls": favicon_urls
            }
        
        else:
            raise Exception(f"API 호출 실패: {response.status_code}")
