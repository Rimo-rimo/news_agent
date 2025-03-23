import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import re
import base64
import urllib.parse
import requests
from bs4 import BeautifulSoup
import os
import dotenv
from streamlit_lottie import st_lottie
import time
import json

dotenv.load_dotenv()

APPFILEPATH = os.getenv("APPFILEPATH")


def render_home():
    home_container = stylable_container(
        key="container_with_border",
        css_styles="""
                {
                    width: 760px;
                    margin: 0 auto;
                }
                """,
    )

    with home_container:
        # SVG 파일 읽기 및 표시
        with open(f"{APPFILEPATH}/data/svg/458.Above-The-Clouds.svg", "rb") as f:
            svg_content = f.read()
            b64 = base64.b64encode(svg_content).decode()
            home_illustration = f'<img src="data:image/svg+xml;base64,{b64}" style="display: block; margin: 0 auto; width: 300px;">'


        with st.container(border=False):
            # home_empty_container = st.container(height=0, border=False)
            home_title_empty = st.empty()
            home_subtitle_empty = st.empty()
            home_query_empty = st.empty()
            home_error_empty = st.empty()

            home_title_empty.markdown(home_illustration, unsafe_allow_html=True)
            home_subtitle_empty.markdown("<h3 style='text-align: center;'>세상 모든 뉴스를 쉽게 이해해 보세요.</h3>", unsafe_allow_html=True)
            input_url = home_query_empty.chat_input("뉴스 link를 입력해 주세요.")

            # URL 형식 검증
            if input_url:
                url_pattern = re.compile(
                    r'^(https?:\/\/)?' # http:// or https://
                    r'(www\.)?' # www.
                    r'([a-zA-Z0-9-]+\.)' # domain name
                    r'([a-zA-Z]{2,})' # domain extension
                    r'(\/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?' # path
                )

                if url_pattern.match(input_url):
                    # 올바른 URL 형식인 경우
                    st.session_state.news_query = input_url
                    st.session_state.page = "content"
                    home_title_empty.empty()
                    home_subtitle_empty.empty()
                    home_query_empty.empty()
                    home_error_empty.empty()
                    st.rerun()
                else:
                    # 잘못된 URL 형식인 경우
                    home_error_empty.error("올바른 URL 형식이 아닙니다. 다시 입력해주세요. (예: https://example.com)")
                    st.session_state.news_query = None