import os
from supabase import create_client, Client
import dotenv

dotenv.load_dotenv()

class DataManager:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
    
    def get_user_newsletters(self, user_id: int):
        """
        Get all newsletters created by a specific user
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of newsletters with their details
        """
        # Join news and newsletters tables to get all newsletters with their associated news
        # Filter by user_id from the news table
        response = (
            self.supabase
            .from_("newsletters")
            .select("id, title, created_at, news_id, news!inner(user_id)")
            .eq("news.user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        
        if not response.data:
            return []
        
        # Format the response to include only necessary data
        newsletters = []
        for item in response.data:
            newsletters.append({
                "id": item["id"],
                "title": item["title"],
                "created_at": item["created_at"],
                "news_id": item["news_id"]
            })
            
        return newsletters
    
    def get_newsletter_by_id(self, newsletter_id: int):
        """
        Get a specific newsletter by its ID
        
        Args:
            newsletter_id: The ID of the newsletter
            
        Returns:
            Newsletter details including related questions and answers
        """
        # Get the newsletter
        newsletter_response = (
            self.supabase
            .from_("newsletters")
            .select("*, news!inner(id, url, content, user_id)")
            .eq("id", newsletter_id)
            .single()
            .execute()
        )
        
        if not newsletter_response.data:
            return None
        
        newsletter = newsletter_response.data
        
        # Get questions related to this news
        questions_response = (
            self.supabase
            .from_("questions")
            .select("id, question")
            .eq("news_id", newsletter["news_id"])
            .execute()
        )
        
        questions = questions_response.data if questions_response.data else []
        
        # Get answers for each question
        for question in questions:
            answer_response = (
                self.supabase
                .from_("answers")
                .select("answer")
                .eq("question_id", question["id"])
                .single()
                .execute()
            )
            
            if answer_response.data:
                question["answer"] = answer_response.data["answer"]
            else:
                question["answer"] = ""
        
        # Combine all data
        result = {
            "id": newsletter["id"],
            "title": newsletter["title"],
            "introduction": newsletter["introduction"],
            "content": newsletter["content"],
            "created_at": newsletter["created_at"],
            "news_id": newsletter["news_id"],
            "news_url": newsletter["news"]["url"],
            "news_content": newsletter["news"]["content"],
            "questions": questions
        }
        
        return result
