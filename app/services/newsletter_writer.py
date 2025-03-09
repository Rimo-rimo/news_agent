from app.config import config
import requests
import json
import codecs
import dotenv
import os
from supabase import create_client, Client
dotenv.load_dotenv()

class NewsletterWriter:
    def __init__(self):
        self.url = config.DIFY_WORKFLOW_API_URL
        self.headers = {
            'Authorization': f'Bearer {config.NEWSLETTER_WRITER_API_KEY}',
            'Content-Type': 'application/json'
        }
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
    def store_newsletter(self, news_id: int, title: str, introduction: str, content: str):
        data = {
            "news_id": news_id,
            "title": title,
            "introduction": introduction,
            "content": content
        }
        
        response = (
            self.supabase.table("newsletters")
            .insert(data)
            .execute()
        )
        
        return response.data[0]["id"]
        
        response = requests.post(self.url, headers=self.headers, json=payload)
    def write_newsletter(self, user_id: int, news_id: int, news_content: str, answers: str, newsletter_title: str, newsletter_introduction: str):
        payload = {
            'inputs': {
                'news_content': news_content,
                'query_answer': answers,
                'newsletter_title': newsletter_title,
                'newsletter_introduction': newsletter_introduction
            },
            'response_mode': 'streaming',
            'user': str(user_id)
        }
    
        response = requests.post(self.url, headers=self.headers, json=payload, stream=True)
        reader = codecs.getreader('utf-8')(response.raw)
        newsletter_content = ""
        for line in reader:
            try:
                if line:
                    decoded_line = line.strip()
                    if decoded_line.startswith('data:'):
                        json_str = decoded_line[5:].strip()
                        if json_str:
                            json_response = json.loads(json_str)
                            if 'data' in json_response and 'text' in json_response['data']:
                                chunk = json_response['data']['text']
                                if chunk:
                                    yield chunk
                                    newsletter_content += chunk
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error processing response: {str(e)}")
                continue
        
        # return full_response
        newsletter_id = self.store_newsletter(news_id, newsletter_title, newsletter_introduction, newsletter_content)
        # return newsletter_id