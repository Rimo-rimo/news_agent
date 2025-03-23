import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from app.services.crawl_agent import CrawlAgent
from app.services.pre_news_agent import PreNewsAgent
from app.services.search_agent import SearchAgent
from app.services.newsletter_writer import NewsletterWriter
import datetime
from app.streamlit.components.icon import icon_dict
import os
import dotenv
import base64
from streamlit_lottie import st_lottie
import json

dotenv.load_dotenv()

APPFILEPATH = os.getenv("APPFILEPATH")

def render_content(user_info, text_font_size):
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

    # Initial content generation
    with content_container:
        with st.container(border=False):
            with st.spinner("##### 뉴스를 읽어보고 있어요"):
                read_image_empty = st.empty()
                with read_image_empty:
                    lottie_path = f"{APPFILEPATH}/data/lottie/333.Inspection.json"
                    with open(lottie_path, "r") as f:
                        lottie_json = json.load(f)
                    # 크기 조절 옵션 추가
                    st_lottie(
                        lottie_json,
                        width=300,   # 원하는 너비(픽셀)
                        key="read_lottie_animation"
                    )
                crawl_agent = CrawlAgent()
                crawl_agent_response = crawl_agent.run(user_id=user_info["id"], url=st.session_state.news_query)
                news_id = crawl_agent_response["news_id"]
                news_content = crawl_agent_response["content"]

                pre_news_agent = PreNewsAgent()
                pre_news_response = pre_news_agent.run(
                    user_id=user_info["id"],
                    news_id=news_id,
                    news_content=news_content,
                    question_n=5
                )
                newsletter_title = pre_news_response["title"]
                introduction = pre_news_response["introduction"]
                perplexity_question_ids = pre_news_response["perplexity_question_ids"]
                tavily_question_ids = pre_news_response["tavily_question_ids"]
                perplexity_questions = pre_news_response["perplexity_questions"]
                tavily_questions = pre_news_response["tavily_questions"]
                read_image_empty.empty()

    # Display title and introduction
    with content_container:
        st.markdown(f"<h3 style='text-align: center; color: #333D4B; width: 100%;'>{newsletter_title}</h3>", unsafe_allow_html=True)
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
                st.markdown(f"<div style='color: #191F28; line-height: 1.8; font-size: {text_font_size}px;'>{introduction}</div>", unsafe_allow_html=True)

        st.text(" ")
        st.text(" ")

    # Q&A section
    with qa_container:
        with st.container(border=False):
            status_ment = st.empty()
            search_image_empty = st.empty()
            perplexity_question_empties = [st.empty() for _ in range(len(perplexity_questions))]
            for i, perplexity_question_empty in enumerate(perplexity_question_empties):
                with perplexity_question_empty:
                    with st.expander(f"Q. :grey[{perplexity_questions[i]}]"):
                        st.markdown("생성 중입니다.")
            
            with search_image_empty:
                lottie_path = f"{APPFILEPATH}/data/lottie/268.Vocabulary.json"
                with open(lottie_path, "r") as f:
                    lottie_json = json.load(f)
                # 크기 조절 옵션 추가
                st_lottie(
                    lottie_json,
                    width=300,   # 원하는 너비(픽셀)
                    key="search_lottie_animation"
                )

            with status_ment:
                with st.spinner("##### 아래 궁금증도 함께 조사해 볼게요!"):
                    search_agent = SearchAgent()
                    search_agent_response = search_agent.run(
                        user_id=user_info["id"],
                        perplexity_questions=perplexity_questions,
                        tavily_questions=tavily_questions,
                        perplexity_question_ids=perplexity_question_ids,
                        tavily_question_ids=tavily_question_ids,
                        news_id=news_id
                    )
                    perplexity_answers = search_agent_response["perplexity_answers"]
                    tavily_answers = search_agent_response["tavily_answers"]
                    tavily_images = search_agent_response["tavily_images"]
                    urls = search_agent_response["urls"]
                    
            search_image_empty.empty()
            status_ment.markdown(f"### {icon_dict['q']} 아래 궁금증을 해결해 봤어요!", unsafe_allow_html=True)
            # f'### {icon_dict[icon_key]}'
            for i, perplexity_question_empty in enumerate(perplexity_question_empties):
                with perplexity_question_empty:
                    with st.expander(f"Q. :grey[{perplexity_questions[i]}]"):
                        st.markdown(perplexity_answers[i], unsafe_allow_html=True)

    # Newsletter generation
    with newsletter_container:
        with st.container(border=False):
            # 가로 스크롤 가능한 영역
            favicon_urls = search_agent_response["favicon_urls"]
            url_titles = search_agent_response["url_titles"]
            urls = search_agent_response["urls"]
            
            # 파비콘과 URL을 함께 표시
            url_popover_test = f"""![favicon]({favicon_urls[0]}) ![favicon]({favicon_urls[1]}) ![favicon]({favicon_urls[2]}) ![favicon]({favicon_urls[3]}) ![favicon]({favicon_urls[4]}) 총 **{len(urls)}**개의 기사를 분석했어요."""
            with st.popover(url_popover_test, use_container_width=True):
                for url, favicon_url, title in zip(urls, favicon_urls, url_titles):
                    st.markdown(
                        f'<div style="display: flex; align-items: center; margin-bottom: 5px;">'
                        f'<img src="{favicon_url}" style="margin-right: 5px; width: 20px; height: 20px;">'
                        f'<a href="{url}" style="text-decoration: none; color: #000000;">{title}</a>'
                        f'</div>',
                        unsafe_allow_html=True
                        )
            # 이미지 표시
            image_cards = ""
            for tavily_image in tavily_images:
                image_cards += f"""
                    <div style="flex: 0 0 auto; width: 300px; height: 200px; margin-right: 10px; text-align: center;"><img src="{tavily_image['url']}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px; border: 2px solid #000000;"></div>"""
            
            st.markdown(f"""<div style="display: flex; overflow-x: auto; white-space: nowrap; padding: 10px 0;">{image_cards}</div>""", unsafe_allow_html=True)
            st.text(" ")
            st.text(" ")
            
            news_placeholder = st.empty()
            
            with st.spinner("##### 뉴스레터를 작성 중이에요."):
                write_image_empty = st.empty()
                with write_image_empty:
                    # lottie 파일 로드
                    lottie_path = f"{APPFILEPATH}/data/lottie/307.Writing.json"
                    with open(lottie_path, "r") as f:
                        lottie_json = json.load(f)
                    # 크기 조절 옵션 추가
                    st_lottie(
                        lottie_json,
                        width=300,   # 원하는 너비(픽셀)
                        key="write_lottie_animation"
                    )
                full_response = "\n"
                newsletter_writer = NewsletterWriter()
                
                answers = []
                for question, answer in zip(perplexity_questions, perplexity_answers):
                    answers.append({"question": question, "answer": answer})
                    
                for question, answer in zip(tavily_questions, tavily_answers):
                    answers.append({"question": question, "answer": answer})
                    
                icon_index = 1  # 아이콘 인덱스 초기화
                for chunk in newsletter_writer.run(
                    user_id=user_info["id"],
                    news_id=news_id,
                    news_content=news_content,
                    answers=str(answers),
                    newsletter_title=newsletter_title,
                    newsletter_introduction=introduction
                ):
                    # ### 패턴을 찾아서 아이콘 추가
                    if '###' in chunk:
                        # icon_dict에서 사용할 수 있는 아이콘 개수를 초과하지 않도록 함
                        icon_key = f"icon_{min(icon_index, 18)}"
                        chunk = chunk.replace('###', f'### {icon_dict[icon_key]}')
                        icon_index += 1
                    
                    full_response += chunk
                    news_placeholder.markdown(
                        f"""<div style='color: #3E4550; line-height: 1.8; font-size: {text_font_size}px;'>
                        {full_response}</div>""",
                        unsafe_allow_html=True
                    )
                write_image_empty.empty()
        st.text(" ")
        st.text(" ")
        st.text(" ") 