import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from app.services.data_manager import DataManager
import datetime
from app.streamlit.components.icon import icon_dict
import urllib.parse
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import ast
import json


def render_view_content(user_info, text_font_size):
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
    
    # Display newsletter content
    with newsletter_container:
        with st.container(border=False):
                # 인용 URL들 가져오기
            if 'citations' in newsletter:
                citation_urls = ast.literal_eval(newsletter['citations'][0]['urls'])
                citation_titles = ast.literal_eval(newsletter['citations'][0]['titles'])
                favicon_urls = []
                for url in citation_urls:
                    parsed_url = urllib.parse.urlparse(url)
                    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
                    favicon_urls.append(favicon_url)
                # st.write(ast.literal_eval(newsletter['citations'][0]['urls']))
            
            # 이미지 URL 가져오기
            if 'image_urls' in newsletter:
                tavily_images = []
                for img_record in newsletter['image_urls']:
                    try:
                        # 전체 urls 문자열을 파싱
                        img_list = ast.literal_eval(img_record['urls'])
                        # 파싱된 리스트의 각 항목을 tavily_images에 추가
                        for img in img_list:
                            if 'url' in img:
                                tavily_images.append({'url': img['url']})
                    except (ValueError, SyntaxError) as e:
                        # 파싱 오류 발생 시 로그만 남기고 계속 진행
                        print(f"Error parsing image URL: {e}")
                        continue

            if citation_urls or tavily_images:
                st.text(" ")
                st.text(" ")
                
                # URL 정보 표시
                if citation_urls:
                    # 파비콘과 URL을 함께 표시
                    url_popover_test = f"""![favicon]({favicon_urls[0]}) ![favicon]({favicon_urls[1]}) ![favicon]({favicon_urls[2]}) ![favicon]({favicon_urls[3]}) ![favicon]({favicon_urls[4]}) 총 **{len(citation_urls)}**개의 기사를 분석했어요."""
                    with st.popover(url_popover_test, use_container_width=True):
                        for url, favicon_url, title in zip(citation_urls, favicon_urls, citation_titles):
                            st.markdown(
                                f'<div style="display: flex; align-items: center; margin-bottom: 5px;">'
                                f'<img src="{favicon_url}" style="margin-right: 5px; width: 20px; height: 20px;">'
                                f'<a href="{url}" style="text-decoration: none; color: #000000;">{title}</a>'
                                f'</div>',
                                unsafe_allow_html=True
                                )
                
                # 이미지 표시
                if tavily_images:
                    image_cards = ""
                    for tavily_image in tavily_images:
                        image_cards += f"""
                            <div style="flex: 0 0 auto; width: 300px; height: 200px; margin-right: 10px; text-align: center;"><img src="{tavily_image['url']}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px; border: 2px solid #000000;"></div>"""
                    
                    st.markdown(f"""<div style="display: flex; overflow-x: auto; white-space: nowrap; padding: 10px 0;">{image_cards}</div>""", unsafe_allow_html=True)
            # Process content to ensure icons are displayed correctly
            st.text(" ")
            st.text(" ")
            full_content = "\n" + newsletter['content']
            
            # Replace headers with icon headers if they don't already have icons
            icon_index = 1
            lines = full_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('###') and not any(icon in line for icon in icon_dict.values()):
                    icon_key = f"icon_{min(icon_index, 18)}"
                    lines[i] = line.replace('###', f'### {icon_dict[icon_key]}')
                    icon_index += 1
            
            full_content = '\n'.join(lines)
            
            # Display the content
            st.markdown(
                f"""<div style='color: #3E4550; line-height: 1.8; font-size: {text_font_size}px;'>
                {full_content}</div>""",
                unsafe_allow_html=True
            )
    
    st.text(" ")
    st.text(" ")
    
    # Prepare questions and answers for display
    questions = []
    
    # Combine perplexity and tavily questions/answers
    if 'perplexity_questions' in newsletter and 'perplexity_answers' in newsletter:
        for q in newsletter['perplexity_questions']:
            answer = next((a['answer'] for a in newsletter['perplexity_answers'] if a['question_id'] == q['id']), None)
            if answer:
                questions.append({"question": q['question'], "answer": answer})
    
    # Display Q&A section
    with qa_container:
        with st.container(border=False):
            st.text(" ")
            st.markdown(f"### {icon_dict['q']} 아래 궁금증을 해결해 봤어요!", unsafe_allow_html=True)
            
            # Display each question and answer
            for question in questions:
                with st.expander(f"Q. :grey[{question['question']}]"):
                    st.markdown(question['answer'], unsafe_allow_html=True)
    
    st.text(" ")
    st.text(" ")
