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
svg_width = 500

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
        st.text(" ")
        st.text(" ")
        container_1 = st.container(border=False)
        st.text(" ")
        st.text(" ")
        container_2 = st.container(border=False)
        st.text(" ")
        st.text(" ")
        container_3 = st.container(border=False)
        
        with container_0:
            st.title("AI 뉴스 자동 생성")
            st.write("AI 뉴스 자동 생성 페이지입니다.")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("sdf")
            with col2:
                st.video(f"{APPFILEPATH}/../dummy/test.mp4")

        with container_1:
            col1, col2 = st.columns([2, 1])
            with col1:
                with st.container(border=False):
                    st.title("AI 뉴스 자동 생성") 
                    st.write("AI 뉴스 자동 생성 페이지입니다.")
            with col2:
                with st.container(border=False):
                    with open(f"{APPFILEPATH}/data/svg/310.Fast-Internet.svg", "rb") as f:
                        svg_content = f.read()
                        b64 = base64.b64encode(svg_content).decode()
                        home_illustration = f'<img src="data:image/svg+xml;base64,{b64}" style="display: block; margin: 0 auto; width: {svg_width}px;">'
                        st.markdown(home_illustration, unsafe_allow_html=True)
        with container_2:
            col1, col2 = st.columns([1, 2])
            with col1:
                with st.container(border=False):
                    with open(f"{APPFILEPATH}/data/svg/523.Music-On.svg", "rb") as f:
                        svg_content = f.read()
                        b64 = base64.b64encode(svg_content).decode()
                        home_illustration = f'<img src="data:image/svg+xml;base64,{b64}" style="display: block; margin: 0 auto; width: {svg_width}px;">'
                        st.markdown(home_illustration, unsafe_allow_html=True)
            with col2:
                with st.container(border=False):
                    st.title("AI 뉴스 자동 생성")
                    st.write("AI 뉴스 자동 생성 페이지입니다.")
        with container_3:
            col1, col2 = st.columns([2, 1])
            with col1:
                with st.container(border=False):
                    st.title("AI 뉴스 자동 생성")
                    st.write("AI 뉴스 자동 생성 페이지입니다.")
            with col2:
                with st.container(border=False):
                    with open(f"{APPFILEPATH}/data/svg/222.Exploring.svg", "rb") as f:
                        svg_content = f.read()
                        b64 = base64.b64encode(svg_content).decode()
                        home_illustration = f'<img src="data:image/svg+xml;base64,{b64}" style="display: block; margin: 0 auto; width: {svg_width}px;">'
                        st.markdown(home_illustration, unsafe_allow_html=True)
        
        