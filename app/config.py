import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CRAWL_AGENT_API_KEY = os.getenv("CRAWL_AGENT_API_KEY")
    QUESTION_GENERATOR_API_KEY = os.getenv("QUESTION_GENERATOR_API_KEY")
    SEARCH_AGENT_API_KEY = os.getenv("SEARCH_AGENT_API_KEY")
    NEWSLETTER_WRITER_API_KEY = os.getenv("NEWSLETTER_WRITER_API_KEY")
    DIFY_WORKFLOW_API_URL = os.getenv("DIFY_WORKFLOW_API_URL")
    
    
config = Config()