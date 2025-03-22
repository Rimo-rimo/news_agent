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
        Get a newsletter and all related data by its ID
        
        Args:
            newsletter_id: The ID of the newsletter
            
        Returns:
            Dictionary containing the newsletter and all related data including
            title, introduction, content, questions, answers, and citations
        """
        # First get the newsletter data
        newsletter_response = (
            self.supabase
            .from_("newsletters")
            .select("*, news_id")
            .eq("id", newsletter_id)
            .execute()
        )
        
        if not newsletter_response.data:
            return None
        
        newsletter = newsletter_response.data[0]
        news_id = newsletter["news_id"]
        
        # Get original news content
        news_response = (
            self.supabase
            .from_("news")
            .select("*")
            .eq("id", news_id)
            .execute()
        )
        
        if news_response.data:
            newsletter["news"] = news_response.data[0]
        
        # Get perplexity questions
        perplexity_questions_response = (
            self.supabase
            .from_("perplexity_questions")
            .select("*")
            .eq("news_id", news_id)
            .execute()
        )
        
        if perplexity_questions_response.data:
            newsletter["perplexity_questions"] = perplexity_questions_response.data
            
            # Get corresponding perplexity answers
            question_ids = [q["id"] for q in perplexity_questions_response.data]
            perplexity_answers_response = (
                self.supabase
                .from_("perplexity_answers")
                .select("*")
                .in_("question_id", question_ids)
                .execute()
            )
            
            if perplexity_answers_response.data:
                newsletter["perplexity_answers"] = perplexity_answers_response.data
        
        # Get tavily questions
        tavily_questions_response = (
            self.supabase
            .from_("tavily_questions")
            .select("*")
            .eq("news_id", news_id)
            .execute()
        )
        
        if tavily_questions_response.data:
            newsletter["tavily_questions"] = tavily_questions_response.data
            
            # Get corresponding tavily answers
            question_ids = [q["id"] for q in tavily_questions_response.data]
            tavily_answers_response = (
                self.supabase
                .from_("tavily_answers")
                .select("*")
                .in_("question_id", question_ids)
                .execute()
            )
            
            if tavily_answers_response.data:
                newsletter["tavily_answers"] = tavily_answers_response.data
        
        # Get citations
        citations_response = (
            self.supabase
            .from_("citations")
            .select("*")
            .eq("news_id", news_id)
            .execute()
        )
        
        if citations_response.data:
            newsletter["citations"] = citations_response.data
            
        # Get image URLs
        image_urls_response = (
            self.supabase
            .from_("image_urls")
            .select("*")
            .eq("news_id", news_id)
            .execute()
        )
        
        if image_urls_response.data:
            newsletter["image_urls"] = image_urls_response.data
            
        return newsletter
