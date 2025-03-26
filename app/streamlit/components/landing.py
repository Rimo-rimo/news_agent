import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_extras.stylable_container import stylable_container
import requests
import json
import base64
import os
import dotenv

dotenv.load_dotenv()

APPFILEPATH = os.getenv("APPFILEPATH")
svg_width = 300

def load_svg(svg_title, svg_width=svg_width, center=True):
    with open(f"{APPFILEPATH}/data/svg/{svg_title}", "rb") as f:
        svg_content = f.read()
        b64 = base64.b64encode(svg_content).decode()
    if center:
        image_svg = f'<img src="data:image/svg+xml;base64,{b64}" style="display: block; margin: 0 auto; width: {svg_width}px;">'
    else:
        image_svg = f'<img src="data:image/svg+xml;base64,{b64}" style="width: {svg_width}px;">'
    return image_svg

svg_dict = {
    "swing": load_svg("swing.svg", 300, center=True),
    "search": load_svg("search.svg", 200, center=True),
    "read": load_svg("read.svg", 300, center=False),
    "mz": load_svg("mz.svg", 200, center=True),
    "qurious": load_svg("qurious.svg", 180, center=False),
    "chat": load_svg("chat.svg", 300, center=True)
}

def render_landing():
    """랜딩 페이지 렌더링"""
    landing_container = stylable_container(
        key="landing_container",
        css_styles="""
                {
                    width: 1000px;
                    margin: 0 auto;
                }
                """,
    )
    with landing_container:
        container_0 = st.container(border=False)
        with st.empty():
            _ = st.container(border=False, height=100)
        container_1 = st.container(border=False)
        with st.empty():
            _ = st.container(border=False, height=100)
        container_2 = st.container(border=False)
        with st.empty():
            _ = st.container(border=False, height=60)
        container_3 = st.container(border=False)
        with st.empty():
            _ = st.container(border=False, height=60)
        container_4 = st.container(border=False)
        with st.empty():
            _ = st.container(border=False, height=100)
        container_5 = st.container(border=False)
        with st.empty():
            _ = st.container(border=False, height=100)

        # 첫번째 컨테이너
        with container_0:
            st.markdown("<h1 style='text-align: center;'>어려운 뉴스는 던져 주세요, 뉴스레터로 돌려 드릴게요</h1>", unsafe_allow_html=True)
            with st.empty():
                _ = st.container(border=False, height=100)
            col1, col2 = st.columns([1, 3])
            with col1:
                with st.empty():
                    _ = st.container(border=False, height=120)
                st.markdown(svg_dict["swing"], unsafe_allow_html=True)
            with col2:
                st.image(f"{APPFILEPATH}/data/image/head.png")
                
        # 두번째 컨테이너
        with container_1:
            st.markdown("<h3 style='text-align: center;'>간단히 링크 하나만 던져주세요.</h3>", unsafe_allow_html=True)
            st.markdown(svg_dict["search"], unsafe_allow_html=True)
            
        # 세번째 컨테이너
        with container_2:
            col1, col2 = st.columns([1, 1.5])
            with col1:
                st.markdown("<h3>하나의 뉴스라도,<br> 다각도로 조사해 볼거에요.</h3>", unsafe_allow_html=True)
                with st.empty():
                    _ = st.container(border=False, height=40)
                st.markdown(svg_dict["read"], unsafe_allow_html=True)
            with col2:
                st.image(f"{APPFILEPATH}/data/image/content_1.png")
        
        with container_3:
            col1, col2 = st.columns([1, 1.5])
            with col1:
                st.markdown("<h3>사회초년생도 단숨에,<br> 이해할 수 있는 수준으로.</h3>", unsafe_allow_html=True)
                with st.empty():
                    _ = st.container(border=False, height=30)
                st.markdown(svg_dict["mz"], unsafe_allow_html=True)
            with col2:
                st.image(f"{APPFILEPATH}/data/image/content_2.png")
                
        with container_4:
            col1, col2 = st.columns([1, 1.5])
            with col1:
                st.markdown("<h3>호기심이 많은 당신을 위해,</h3>", unsafe_allow_html=True)
                with st.empty():
                    _ = st.container(border=False, height=6)
                st.markdown(svg_dict["qurious"], unsafe_allow_html=True)
            with col2:
                st.image(f"{APPFILEPATH}/data/image/content_3.png")
                
        with container_5:
            st.markdown("<h3 style='text-align: center;'>하루 5분,<br> 대화에 써먹을 지식 한 스푼 어떠세요?</h3>", unsafe_allow_html=True)
            st.markdown(svg_dict["chat"], unsafe_allow_html=True)
            