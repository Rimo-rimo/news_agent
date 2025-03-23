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
from app.streamlit.components.view_content import render_view_content

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
    if st.session_state.page == "view_content":
        render_view_content(user_info, text_font_size)