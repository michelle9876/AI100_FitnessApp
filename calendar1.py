import streamlit as st
import calendar
from datetime import datetime, timedelta

# 현재 날짜 가져오기
now = datetime.now()
if 'current_year' not in st.session_state:
    st.session_state.current_year = now.year
if 'current_month' not in st.session_state:
    st.session_state.current_month = now.month
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'Monthly'

current_year = st.session_state.current_year
current_month = st.session_state.current_month
view_mode = st.session_state.view_mode
today = now.day

# 이전/다음 달 버튼
def prev_month(year, month):
    if month == 1:
        return year - 1, 12
    else:
        return year, month - 1

def next_month(year, month):
    if month == 12:
        return year + 1, 1
    else:
        return year, month + 1

prev_year, prev_month = prev_month(current_year, current_month)
next_year, next_month = next_month(current_year, current_month)

col1, col2, col3, col4 = st.columns([0.1, 0.1, 1, 0.1])
with col1:
    if st.button("◀", key='prev_button'):
        st.session_state.current_year, st.session_state.current_month = prev_year, prev_month
        st.experimental_rerun()
with col2:
    if st.button("▶", key='next_button'):
        st.session_state.current_year, st.session_state.current_month = next_year, next_month
        st.experimental_rerun()
with col3:
    m_col, w_col = st.columns([1, 1])
    with m_col:
        if st.button("Monthly", key='monthly'):
            st.session_state.view_mode = 'Monthly'
            st.experimental_rerun()
    with w_col:
        if st.button("Weekly", key='weekly'):
            st.session_state.view_mode = 'Weekly'
            st.experimental_rerun()

# 월간 달력 표시
def create_monthly_calendar(year, month, today):
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)

    days_in_week = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    
    # 요일 헤더 표시
    cols = st.columns(7)
    for i, day in enumerate(days_in_week):
        cols[i].markdown(f"<div style='text-align: center; color: white; background-color: lightpink;'>{day}</div>", unsafe_allow_html=True)

    # 달력 표시
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].markdown(f"<div style='height: 50px; border: 1px solid lightgrey;'></div>", unsafe_allow_html=True)
            elif day == today and year == now.year and month == now.month:
                cols[i].markdown(f"<div style='height: 50px; text-align: center; background-color: lightblue; border: 1px solid lightgrey;'>{day}</div>", unsafe_allow_html=True)
            else:
                cols[i].markdown(f"<div style='height: 50px; text-align: center; background-color: #f0f8ff; border: 1px solid lightgrey;'>{day}</div>", unsafe_allow_html=True)

# 주간 플래너 표시
def create_weekly_planner(year, month):
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)
    days_in_week = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    st.write(f"### {year}년 {month}월")
    for week_number, week in enumerate(month_days, 1):
        week_dates = [f"{month}/{day}" if day != 0 else "" for day in week]
        week_start = next((date for date in week_dates if date), "")
        week_end = next((date for date in reversed(week_dates) if date), "")
        week_range = f"{week_start} - {week_end}" if week_start and week_end else ""

        st.markdown(f"#### <div style='text-align: center;'>{week_number}주차 ({week_range})</div>", unsafe_allow_html=True)
        cols = st.columns(7)
        for i, day in enumerate(week_dates):
            cols[i].markdown(f"<div style='text-align: center; border: 1px solid lightgrey; padding: 10px;'>{days_in_week[i]}<br>{day}</div>", unsafe_allow_html=True)

st.header(f"{current_year}년 {current_month}월")
if st.session_state.view_mode == 'Monthly':
    create_monthly_calendar(current_year, current_month, today)
else:
    create_weekly_planner(current_year, current_month)