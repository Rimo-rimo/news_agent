import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.stylable_container import stylable_container
from app.services.user_manager import UserManager
import yaml
from yaml.loader import SafeLoader

def setup_auth(config):
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
                    signup_username = st.text_input("Username")
                    signup_password = st.text_input("Password", type="password")
                    signup_password_repeat = st.text_input("Password Check", type="password")
                    signup_button = st.button("가입하기", use_container_width=True, type="primary")

                    if signup_button:
                        handle_signup(signup_username, signup_password, signup_password_repeat, config)
    
    # Return authenticator so it can be used for logout
    return authenticator

def handle_signup(username, password, password_repeat, config):
    if not username or not password or not password_repeat:
        st.error("모든 필드를 입력해주세요.")
        st.toast('모든 필드를 입력해주세요!', icon='😅')
    elif password != password_repeat:
        st.error("비밀번호가 일치하지 않습니다.")
        st.toast('비밀번호가 일치하지 않습니다!', icon='😅')
    elif username in config['credentials']['usernames']:
        st.error("이미 사용 중인 사용자명입니다.")
        st.toast('이미 사용 중인 사용자명입니다!', icon='😅')
    elif len(password) < 4:
        st.error("비밀번호는 최소 4자 이상이어야 합니다.")
        st.toast('비밀번호는 최소 4자 이상이어야 합니다!', icon='😅')
    else:
        try:
            user_manager = UserManager()
            user_manager.signup_user(username, password)
            st.success("회원가입이 완료되었습니다!")
            st.toast('회원가입이 완료되었습니다!', icon='🥳')
            st.balloons()
        except Exception as e:
            st.error(f"회원가입 중 오류가 발생했습니다: {e}")
            print(e)