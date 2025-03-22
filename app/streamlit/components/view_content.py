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

def get_page_title(url):
    try:
        # 타임아웃을 짧게 설정하여 응답 지연 방지
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 페이지 제목 가져오기
            title = soup.title.string if soup.title else None
            
            # 제목이 너무 길면 자르기
            if title and len(title) > 50:
                title = title[:36] + "..."
                
            return title if title else urllib.parse.urlparse(url).netloc
        return urllib.parse.urlparse(url).netloc
    except Exception as e:
        # 오류 발생 시 도메인 이름 반환
        return urllib.parse.urlparse(url).netloc 

def get_page_titles_parallel(urls, max_workers=30):
    """여러 URL의 페이지 제목을 병렬로 가져옵니다."""
    titles = [None] * len(urls)
    favicon_urls = [None] * len(urls)
    
    def process_url(index_url):
        index, url = index_url
        parsed_url = urllib.parse.urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
        title = get_page_title(url)
        return index, title, favicon_url
    
    # 병렬로 URL 처리
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # URL과 인덱스를 함께 전달
        results = executor.map(process_url, enumerate(urls))
        
        # 결과 저장
        for index, title, favicon_url in results:
            titles[index] = title
            favicon_urls[index] = favicon_url
            
    return titles, favicon_urls 

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
        
        st.text(" ")
        st.text(" ")
    
    # Display newsletter content
    with newsletter_container:
        with st.container(border=False):
            # Process content to ensure icons are displayed correctly
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
    
    # 출처 링크 및 이미지 표시 부분 추가
    # urls = []
    # tavily_images = []
    
    # # 인용 URL들 가져오기
    # if 'citations' in newsletter:
    #     urls = [citation['url'] for citation in newsletter['citations'] if 'url' in citation]
    
    # # 이미지 URL 가져오기
    # if 'image_urls' in newsletter:
    #     tavily_images = [{'url': ast.literal_eval(img)['url']} for img in newsletter['image_urls']]
    
    # # 이미지와 URL 정보 표시
    
    # if urls or tavily_images:
    #     st.text(" ")
    #     st.text(" ")
        
    #     # URL 정보 표시
    #     if urls:
    #         url_titles, favicon_urls = get_page_titles_parallel(urls)
    #         # 파비콘과 URL을 함께 표시
    #         url_popover_text = f"""![favicon]({favicon_urls[0]})"""
    #         if len(favicon_urls) > 1:
    #             for i in range(1, min(5, len(favicon_urls))):
    #                 url_popover_text += f""" ![favicon]({favicon_urls[i]})"""
    #         url_popover_text += f""" 총 **{len(urls)}**개의 기사를 분석했어요."""
            
    #         with st.popover(url_popover_text, use_container_width=True):
    #             for url, favicon_url, title in zip(urls, favicon_urls, url_titles):
    #                 st.markdown(
    #                     f'<div style="display: flex; align-items: center; margin-bottom: 5px;">'
    #                     f'<img src="{favicon_url}" style="margin-right: 5px; width: 20px; height: 20px;">'
    #                     f'<a href="{url}" style="text-decoration: none; color: #000000;">{title}</a>'
    #                     f'</div>',
    #                     unsafe_allow_html=True
    #                 )
        
        # # 이미지 표시
        # if tavily_images:
        #     image_cards = ""
        #     for tavily_image in tavily_images:
        #         image_cards += f"""
        #             <div style="flex: 0 0 auto; width: 300px; height: 200px; margin-right: 10px; text-align: center;"><img src="{tavily_image['url']}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px; border: 2px solid #000000;"></div>"""
            
        #     st.markdown(f"""<div style="display: flex; overflow-x: auto; white-space: nowrap; padding: 10px 0;">{image_cards}</div>""", unsafe_allow_html=True)
    
    # Display Q&A section
    with qa_container:
        with st.container(border=False):
            st.markdown(f"### {icon_dict['q']} 아래 궁금증을 해결해 봤어요!", unsafe_allow_html=True)
            
            # Display each question and answer
            for question in questions:
                with st.expander(f"Q. :grey[{question['question']}]"):
                    st.markdown(question['answer'], unsafe_allow_html=True)
    
    st.text(" ")
    st.text(" ")
