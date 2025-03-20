####################################################################################
# streamlit run ai_news.py --server.port 8501
####################################################################################

import streamlit as st
import streamlit_authenticator as stauth
from app.services.pre_news_agent import PreNewsAgent
from app.services.search_agent import SearchAgent
from app.services.newsletter_writer import NewsletterWriter
from app.services.crawl_agent import CrawlAgent
from app.services.data_manager import DataManager
from streamlit_extras.stylable_container import stylable_container
import streamlit.components.v1 as components
import json
import time
import requests
import json
import yaml
from yaml.loader import SafeLoader
import codecs
import datetime
import re
import uuid
from app.services.user_manager import UserManager

st.set_page_config(page_title="Owl Letter",layout="wide", page_icon="🦉",initial_sidebar_state="collapsed")
st.logo(image="./data/logo.svg", 
        size="small"
        )

# ############## dify chatbot ui ##############
# # HTML 코드 정의
# dify_chatbot_code = """
# <iframe
#  src="https://udify.app/chatbot/jH3bBdYf2zDVuUNs"
#  style="width: 100%; height: 400px;
#  frameborder="0"
#  allow="microphone">
# </iframe>
# """

# # Streamlit에 HTML 컴포넌트로 삽입
# components.html(dify_chatbot_code, height=600, width=800)
# ############## dify chatbot ui ##############

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


auth_container = stylable_container(
        key="container_with_border",
        css_styles="""
                {
                    width: 500px; 
                    margin: 0 auto;
                }
                """,
    )

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

if not st.session_state['authentication_status']:
    with auth_container:
        with st.container(border=False):
            authenticator.login(location='main', fields={'Form name': 'Login', 'Username': 'Username', 'Password': 'Password', 'Login': 'Login'})
            if st.session_state['authentication_status']:
                pass
            elif st.session_state['authentication_status'] is False:
                st.error('Username/Password 를 다시 확인해주세요.')
            
            # 회원가입 버튼
            with st.expander("Sign-Up"):
                # 입력 필드
                signup_username = st.text_input("Username")
                signup_password = st.text_input("Password", type="password")
                signup_password_repeat = st.text_input("Password Check", type="password")
                # 제출 및 취소 버튼
                signup_button = st.button("가입하기", use_container_width=True, type="primary")

                # 회원가입 로직 구현
                if signup_button:
                    # 1. 모든 필드가 입력되었는지 확인
                    if not signup_username or not signup_password or not signup_password_repeat:
                        st.error("모든 필드를 입력해주세요.")
                        st.toast('모든 필드를 입력해주세요!', icon='😅')
                    # 2. 비밀번호 일치 확인
                    elif signup_password != signup_password_repeat:
                        st.error("비밀번호가 일치하지 않습니다.")
                        st.toast('비밀번호가 일치하지 않습니다!', icon='😅')
                    # 3. 사용자명 중복 확인
                    elif signup_username in config['credentials']['usernames']:
                        st.error("이미 사용 중인 사용자명입니다.")
                        st.toast('이미 사용 중인 사용자명입니다!', icon='😅')
                    # 4. 비밀번호 복잡성 검사 (최소 4자 이상)
                    elif len(signup_password) < 4:
                        st.error("비밀번호는 최소 4자 이상이어야 합니다.")
                        st.toast('비밀번호는 최소 4자 이상이어야 합니다!', icon='😅')
                    else:
                        try:
                            # Use UserManager to create user in Supabase
                            user_manager = UserManager()
                            # Create user in Supabase and get the auto-generated ID
                            user_manager.signup_user(signup_username, signup_password)

                            # 10. 성공 메시지 표시
                            st.success("회원가입이 완료되었습니다!")
                            st.toast('회원가입이 완료되었습니다!', icon='🥳')
                            st.balloons()
                        except Exception as e:
                            st.error(f"회원가입 중 오류가 발생했습니다: {e}")
                            print(e)

if st.session_state['authentication_status']:
    user_name = st.session_state['username']
    user_info = config['credentials']['usernames'][user_name]
    
    # sidebar
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
                                background-color: #FCD27A;
                                transform: translateY(-3px);
                                cursor: pointer;
                            }
                            """,
                    ):
                        if st.button(f"{newsletter['title']}", key=f"newsletter_{newsletter['id']}", use_container_width=True):
                            # Store the selected newsletter ID in session state
                            st.session_state.selected_newsletter_id = newsletter['id']
                            st.session_state.page = "view_newsletter"
                            st.rerun()
                
                # Add some space between date groups
                st.text("")

    if "page" not in st.session_state:
        st.session_state.page = "home"

    if "news_query" not in st.session_state:
        st.session_state.news_query = None

    if st.session_state.page == "home":
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
            with st.container(border=False):
                home_empty_container = st.container(height= 100, border=False)
                home_title_empty = st.empty()
                home_subtitle_empty = st.empty()
                home_query_empty = st.empty()
                home_error_empty = st.empty()

                home_title_empty.markdown("<h1 style='text-align: center;'>Owl Letter</h1>", unsafe_allow_html=True)
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
                        # st.error("올바른 URL 형식이 아닙니다. 다시 입력해주세요. (예: https://example.com)")
                        home_error_empty.error("올바른 URL 형식이 아닙니다. 다시 입력해주세요. (예: https://example.com)")
                        st.session_state.news_query = None

    if st.session_state.page == "content":
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
        newsletter_container = stylable_container(
            key="newsletter_container",
            css_styles="""
                    {
                        width: 700px;
                        margin: 0 auto;
                        display: flex;
                    }
                    """,
        )
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
        with content_container: 
            with st.container(border=False):
                # 크롤링 및 질문 생성
                with st.spinner("##### 뉴스를 읽어보고 있어요"):
                    # 크롤링 에이전트로 URL에서 콘텐츠 추출 및 저장
                    crawl_agent = CrawlAgent()
                    crawl_agent_response = crawl_agent.run(user_id=user_info["id"], url=st.session_state.news_query)
                    news_id = crawl_agent_response["news_id"]
                    news_content = crawl_agent_response["content"]

                    # 질문 생성 (이미 저장된 news_id 사용)
                    pre_news_agent = PreNewsAgent()
                    question_generator_response = pre_news_agent.run(
                        user_id=user_info["id"], 
                        news_id=news_id,
                        news_content=news_content, 
                        question_n=5
                    )
                    title = question_generator_response["title"]
                    introduction = question_generator_response["introduction"]
                    perplexity_question_ids = question_generator_response["perplexity_question_ids"]
                    tavily_question_ids = question_generator_response["tavily_question_ids"]
                    perplexity_questions = question_generator_response["perplexity_questions"]
                    tavily_questions = question_generator_response["tavily_questions"]

        with content_container:
            st.markdown(f"<h3 style='text-align: center; color: #333D4B; width: 100%;'>{title}</h3>", unsafe_allow_html=True)
            st.text(" ")
            current_date = datetime.datetime.now().strftime("%Y.%m.%d")
            st.markdown(f"<p style='text-align: center; color: #6B7684; width: 100%;'>{current_date} by {user_info['name']}</p>", unsafe_allow_html=True)
            st.text(" ")

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
                    with st.container(border=False):
                        st.markdown(f"<div style='color: #191F28; line-height: 1.8; font-size: {text_font_size}px;'>{introduction}</div>", unsafe_allow_html=True)

            st.text(" ")
            st.text(" ")

        with qa_container:
            with st.container(border=False):
                status_ment = st.empty()
                perplexity_question_empties = [st.empty() for _ in range(len(perplexity_questions))]
                for i, perplexity_question_empty in enumerate(perplexity_question_empties):
                    with perplexity_question_empty:
                        with st.expander(f"Q. :grey[{perplexity_questions[i]}]"):
                            st.markdown("생성 중입니다.")
                
                with status_ment:
                    with st.spinner("##### :red-background[아래 궁금증도 함께 조사해 볼게요!]"):
                        search_agent = SearchAgent()
                        search_agent_response = search_agent.run(
                            user_id=user_info["id"],
                            perplexity_questions=perplexity_questions,
                            tavily_questions=tavily_questions,
                            perplexity_question_ids=perplexity_question_ids,
                            tavily_question_ids=tavily_question_ids
                        )
                        perplexity_answers = search_agent_response["perplexity_answers"]
                        tavily_answers = search_agent_response["tavily_answers"]
                        perplexity_urls = search_agent_response["perplexity_urls"]
                        tavily_urls = search_agent_response["tavily_urls"]
                        
                status_ment.markdown("##### :red-background[아래 궁금증을 해결해 봤어요!]", unsafe_allow_html=True)
                
                for i, perplexity_question_empty in enumerate(perplexity_question_empties):
                    with perplexity_question_empty:
                        with st.expander(f"Q. :grey[{perplexity_questions[i]}]"):
                            st.markdown(perplexity_answers[i], unsafe_allow_html=True)
                

        with newsletter_container:
            with st.container(border=False):
                # 뉴스레터 전체 내용을 담을 placeholder
                news_placeholder = st.empty()
                
                with st.spinner("##### 뉴스레터를 작성 중이에요."):
                    # 뉴스 생성
                    full_response = "\n"
                    
                    newsletter_writer = NewsletterWriter()
                    
                    answers = []
                    for question, answer in zip(perplexity_questions, perplexity_answers):
                        answers.append(
                            {
                                "question": question,
                                "answer": answer
                            }
                        )
                        
                    for question, answer in zip(tavily_questions, tavily_answers):
                        answers.append(
                            {
                                "question": question,
                                "answer": answer
                            }
                        )
                        
                    # Stream the response
                    for chunk in newsletter_writer.write_newsletter(
                        user_id=user_info["id"], 
                        news_id=news_id, 
                        news_content=news_content,
                        answers=str(answers), 
                        newsletter_title=title, 
                        newsletter_introduction=introduction
                    ):
                        full_response += chunk
                        news_placeholder.markdown(
                                    f"""<div style='color: #3E4550; line-height: 1.8; font-size: {text_font_size}px;'>
                                    {full_response}</div>""", 
                                    unsafe_allow_html=True
                                )
            
            st.text(" ")
            st.text(" ")
            st.text(" ")

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
