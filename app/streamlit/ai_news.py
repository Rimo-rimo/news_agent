####################################################################################
# streamlit run ai_news.py --server.port 8501
####################################################################################

import streamlit as st
from app.services.pre_news_agent import PreNewsAgent
from app.services.search_agent import SearchAgent
from app.services.newsletter_writer import NewsletterWriter
from app.services.crawl_agent import CrawlAgent
from app.services.data_manager import DataManager
from streamlit_extras.stylable_container import stylable_container
import json
import yaml
from yaml.loader import SafeLoader
import datetime
import re
from app.streamlit.auth import setup_auth
from app.streamlit.components.sidebar import render_sidebar
from app.streamlit.components.home import render_home
from app.streamlit.components.content import render_content

# Streamlit Settings
st.set_page_config(page_title="Owl Letter",layout="wide", page_icon="🦉",initial_sidebar_state="collapsed")
st.logo(image="./data/logo.svg", 
        size="small"
        )

if "page" not in st.session_state:
        st.session_state.page = "home"

if "news_query" not in st.session_state:
    st.session_state.news_query = None

text_font_size = 18
hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
        .css-1544g2n {
            background-color: white !important;
        }
        .css-1cypcdb {
            background-color: white !important;
        }
        [data-testid="stSidebarContent"] {
            background-color: white !important;
            border-right: 1px solid #e6e6e6 !important;
        }
        .st-emotion-cache-1cypcdb {
            background-color: white !important;
        }
        .st-emotion-cache-1544g2n {
            background-color: white !important;
        }
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


# ############################# Auth Page #############################
setup_auth(config)

if st.session_state['authentication_status']:
    user_name = st.session_state['username']
    user_info = config['credentials']['usernames'][user_name]
    
    # ############################# Sidebar #############################
    render_sidebar(user_info)

    # ############################# Home #############################
    if st.session_state.page == "home":
        render_home()

    # ############################# Content #############################
    if st.session_state.page == "content":
        render_content(user_info, text_font_size)

    # ############################# View Newsletter #############################
    if st.session_state.page == "view_newsletter":
        # Get the selected newsletter details
        data_manager = DataManager()
        newsletter = data_manager.get_newsletter_by_id(st.session_state.selected_newsletter_id)
            
        if not newsletter:
            st.error("뉴스레터를 찾을 수 없습니다.")
            st.session_state.page = "home"
            st.rerun()
        
        content_container = stylable_container(
            key="content_container",
            css_styles="""
                    {
                        width: 700px;
                        margin: 0 auto;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }
                    """,
        )
        
        with content_container:
            # Display newsletter title and date
            st.markdown(f"<h3 style='text-align: center; color: #333D4B; width: 100%;'>{newsletter['title']}</h3>", unsafe_allow_html=True)
            st.text(" ")
            
            # Format the date from the created_at timestamp
            created_date = datetime.datetime.fromisoformat(newsletter["created_at"].replace("Z", "+00:00")).strftime("%Y.%m.%d")
            st.markdown(f"<p style='text-align: center; color: #6B7684; width: 100%;'>{created_date} by {user_info['name']}</p>", unsafe_allow_html=True)
            st.text(" ")
            
            # Display introduction
            introduction_container = stylable_container(
                key="introduction_container",
                css_styles="""
                        {
                            width: 700px;
                            margin: 0 auto;
                            background-color: #F3F4F6;
                            border-radius: 16px;
                            padding: 30px;
                        }
                        """,
            )
            with introduction_container:
                with st.container(border=False):
                    st.markdown(f"<div style='color: #191F28; line-height: 1.8; font-size: {text_font_size}px;'>{newsletter['introduction']}</div>", unsafe_allow_html=True)
            st.text(" ")
            st.text(" ")
            
            # Display newsletter content
            with st.container(border=False):
                # st.markdown(newsletter['content'], unsafe_allow_html=True)
                st.markdown(f"""
                            <div style='color: #3E4550; line-height: 1.8; font-size: {text_font_size}px;' markdown="1">
                            \n {newsletter['content']}
                            </div>""", unsafe_allow_html=True)
            
            st.text(" ")
            st.text(" ")
                        # Display Q&A section
            qa_container = stylable_container(
                key="qa_container",
                css_styles="""
                        {
                            width: 700px;
                            margin: 0 auto;
                            display: flex;
                        }
                        """,
            )
            
            with qa_container:
                with st.container(border=False):
                    st.markdown("##### :red-background[아래 궁금증을 해결해 봤어요!]", unsafe_allow_html=True)
                    
                    # Display each question and answer
                    for question in newsletter['questions']:
                        with st.expander(f"Q. :grey[{question['question']}]"):
                            st.markdown(question['answer'], unsafe_allow_html=True)
            
            st.text(" ")
            st.text(" ")