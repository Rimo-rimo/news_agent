from app.config import config
import os
from supabase import create_client, Client
import dotenv
import streamlit_authenticator as stauth
import yaml

dotenv.load_dotenv()

class UserManager:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        self.config_path = './config.yaml'

    def store_user(self, username, password_hash):
        """
        Create a new user in Supabase and return the user ID
        """
        # Create user in Supabase
        user_data = {
            "name": username,
            "password_hash": password_hash
        }

        response = (
            self.supabase.table("users")
            .insert(user_data)
            .execute()
        )

        if not response.data:
            raise Exception("Failed to create user in database")

        # Return the auto-generated ID from Supabase
        return response.data[0]["id"]

    def signup_user(self, username, password):
        """
        Update the config.yaml file with the new user
        """
        # Load current config
        with open(self.config_path) as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)

        # Add new user to config
        new_user = {
            "failed_login_attempts": 0,
            "name": username,
            "logged_in": False,
            "password": password,  # Will be hashed later
            "roles": ["user"]
        }

        config['credentials']['usernames'][username] = new_user

        # Hash passwords
        config['credentials'] = stauth.Hasher.hash_passwords(config['credentials'])

        # Get user id
        user_id = self.store_user(username, config['credentials']['usernames'][username]['password'])

        # Update config
        config['credentials']['usernames'][username]['id'] = user_id
        config['credentials'] = stauth.Hasher.hash_passwords(config['credentials'])

        # Save updated config
        with open(self.config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)

        return True
