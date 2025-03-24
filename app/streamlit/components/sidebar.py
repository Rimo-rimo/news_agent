import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from app.services.data_manager import DataManager
import datetime

def render_sidebar(user_info):
    with st.sidebar:
        data_manager = DataManager()
        newsletters = data_manager.get_user_newsletters(user_id=user_info["id"])
        
        # Group newsletters by date
        newsletters_by_date = {}
        for newsletter in newsletters:
            # Convert created_at string to datetime and extract date part
            created_date = datetime.datetime.fromisoformat(newsletter["created_at"].replace("Z", "+00:00")).date()
            
            # Format date as YYYY.MM.DD
            date_str = created_date.strftime("%Y.%m.%d")
            
            # Add to dictionary grouped by date
            if date_str not in newsletters_by_date:
                newsletters_by_date[date_str] = []
            
            newsletters_by_date[date_str].append(newsletter)
        
        # Display home button at the top
        home_button = st.button("Home", use_container_width=True, type="primary")
        if home_button:
            st.session_state.page = "home"
            st.session_state.news_query = None
            st.rerun()
        
        landing_button = st.button("🚀 landing page", use_container_width=True, type="primary")
        if landing_button:
            st.session_state.page = "landing"
            st.rerun()
                
        st.session_state['authenticator'].logout(
            button_name="로그아웃",
            key="logout_button",
            location="sidebar",
            use_container_width=True
        )
        
        st.divider()
        
        # Display newsletters grouped by date
        if not newsletters:
            st.info("아직 생성된 뉴스레터가 없습니다.")
        else:
            for date, date_newsletters in newsletters_by_date.items():
                st.caption(f"**{date}**")
                
                for newsletter in date_newsletters:
                    # Create a button for each newsletter
                    with stylable_container(
                        key="green_button",
                        css_styles="""
                            button {
                                color: #191F28;
                                border-radius: 14px;
                                border: none;
                                margin: 0 auto;
                                background-color: #F3F4F6;
                                padding: 14px;
                                transition: background-color 0.3s, transform 0.2s;
                            }
                            button:hover {
                                background-color: #EEF5FE;
                                transform: translateY(-3px);
                                cursor: pointer;
                            }
                            """,
                    ):
                        if st.button(f"{newsletter['title']}", key=f"newsletter_{newsletter['id']}", use_container_width=True):
                            # Store the selected newsletter ID in session state
                            st.session_state.selected_newsletter_id = newsletter['id']
                            st.session_state.page = "view_content"
                            st.rerun()
                
                # Add some space between date groups
                st.text("") 