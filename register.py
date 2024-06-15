import streamlit as st
import csv
import os

# CSV 파일 경로 설정
CSV_FILE = "users.csv"

# CSV 파일이 없으면 빈 파일 생성 및 헤더 추가
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'password', 'name', 'age', 'gender', 'height', 'weight'])

# 회원가입 폼
def register_form():
    st.subheader("Register")

    with st.form("Register Form"):
        st.header("회원가입 하기")

        user_id = st.text_input("사용자 ID")
        name = st.text_input("이름")
        gender = st.selectbox("성별", ["Male", "Female"])
        password = st.text_input("비밀번호", type="password")

        submit_button = st.form_submit_button(label="회원가입")

    if submit_button:
        if not user_id or not name or not password:
            st.error("모든 필드를 입력하세요.")
        else:
            # 사용자 ID가 이미 존재하는지 확인
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] == user_id:
                        st.error("이미 존재하는 사용자 ID입니다.")
                        return
            
            # 사용자 ID가 존재하지 않으면 CSV 파일에 추가
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([user_id, password, name, "null", gender, "null", "null"])
            
            st.success(f"환영합니다, {name}! 회원가입 성공!")
            st.write("로그인 페이지로 이동합니다...")

            st.session_state['current_page'] = 'Login'
            st.rerun()

# 로그인 폼
def login_form():
    st.subheader("Login")

    with st.form("Login Form"):
        st.header("로그인 하기")

        user_id = st.text_input("아이디")
        user_password = st.text_input("비밀번호", type="password")
        login_button = st.form_submit_button(label="로그인")

    if login_button:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == user_id and row['password'] == user_password:
                    st.success(f"환영합니다, {row['name']}!")
                    st.session_state['logged_in_user'] = user_id
                    st.session_state['current_page'] = 'My Page'
                    st.experimental_rerun()
                    return
            else:
                st.error("잘못된 사용자 ID 또는 비밀번호입니다.")

# 마이 페이지 폼
def my_page_form():
    st.subheader("My Page")

    user_id = st.session_state['logged_in_user']
    user_info = None

    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                user_info = row
                break

    if user_info:
        name = user_info['name']
        gender = user_info['gender']
        age = user_info['age'] if user_info['age'] != "null" else ""
        height = user_info['height'] if user_info['height'] != "null" else ""
        weight = user_info['weight'] if user_info['weight'] != "null" else ""

        with st.form("My Page Form"):
            st.header("내 정보 관리")

            name = st.text_input("이름", value=name)
            gender = st.selectbox("성별", ["Male", "Female"], index=0 if gender == "Male" else 1)
            age = st.text_input("나이", value=age)
            height = st.text_input("키 (cm)", value=height)
            weight = st.text_input("몸무게 (kg)", value=weight)

            submit_button = st.form_submit_button(label="저장")

        if submit_button:
            save_user_info(user_id, name, gender, age or "null", height or "null", weight or "null")
            st.success("정보가 성공적으로 저장되었습니다.")

# 사용자 정보를 CSV 파일에 저장하는 함수
def save_user_info(user_id, name, gender, age, height, weight):
    rows = []
    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                row['name'] = name
                row['gender'] = gender
                row['age'] = age
                row['height'] = height
                row['weight'] = weight
            rows.append(row)
    
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def main():
    st.title("Membership System")

    if 'current_page' not in st.session_state:
        # st.session_state['current_page'] = 'Home'
        st.session_state['current_page'] = 'Register'
    if 'logged_in_user' not in st.session_state:
        st.session_state['logged_in_user'] = None

    # menu = ["Home", "Register", "Login"]
    menu = ["Register", "Login"]
    if st.session_state['logged_in_user']:
        menu.append("My Page")

    choice = st.sidebar.selectbox("Menu", menu, index=menu.index(st.session_state['current_page']))
    st.session_state['current_page'] = choice

    # if st.session_state['current_page'] == "Home":
    #     st.subheader("Home")
    #     st.write("이 앱은 간단한 회원 관리 시스템 기능을 제공합니다.")
    # elif st.session_state['current_page'] == "Register":
    if st.session_state['current_page'] == "Register":
        register_form()
    elif st.session_state['current_page'] == "Login":
        login_form()
    elif st.session_state['current_page'] == "My Page":
        my_page_form()
    

if __name__ == '__main__':
    main()