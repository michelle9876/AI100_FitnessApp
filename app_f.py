import streamlit as st
from pytube import Playlist, YouTube
import csv
import os
from openai import OpenAI
import pandas as pd
from collections import defaultdict
from PIL import Image

os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

CSV_FILENAME = 'videos1.csv'

def is_duplicate(video_id, csv_filename):
    try:
        with open(csv_filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['video_id'] == video_id:
                    return True
    except FileNotFoundError:
        return False
    return False

def get_videos_by_user(user_id, csv_filename):
    videos = []
    try:
        with open(csv_filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == user_id:
                    row['categories'] = row['category'].split(',')
                    videos.append(row)
    except FileNotFoundError:
        pass
    return videos

def categorize_video(title):
    categories_df = pd.read_csv('home_training_categories.csv', header=None, names=['카테고리1', '카테고리2', '카테고리3'])
    categories_df['카테고리'] = categories_df.apply(lambda x: ','.join(x.dropna()), axis=1)
    category_list = categories_df['카테고리'].tolist()

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": title
            },
            {
                "role": "system",
                "content":  f"다음 유저가 입력한 동영상의 제목과 설명을 기반으로 가장 적절한 카테고리를 선택하세요 부위가 있으면 부위와 가장 유사한 값을 찾으세요 응답값은 카테고리를 ,으로 구분해서만 응답하세요 응답형식 '카테고리1, 카테고리2..' :\n제목: {title}🔥\n설명: \n카테고리 후보: {category_list} "
            }
        ],
        model="gpt-4",
    )
    return chat_completion.choices[0].message.content.strip()

def load_videos(csv_filename, user_id):
    try:
        videos = pd.read_csv(csv_filename)
        videos = videos[videos['user_id'] == user_id]
        videos['categories'] = videos['category'].apply(lambda x: x.split(','))
        return videos
    except FileNotFoundError:
        return pd.DataFrame()
    
# 시간을 'NN분 NN초' 형식으로 변환하는 함수
def format_time(seconds):
    seconds = int(seconds)  # 초 값을 정수로 변환
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}분 {seconds}초"

def AL_video(output_string):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": output_string
            },
            {
                "role": "system",
                "content":  f"다음 유저가 입력한 조건에 맞춰 추천된 유튜브 홈트레이닝 영상목록이다 영상은 day별로 나열되어있으며 'Day1 '동영상제목 (시간) - 카테고리', ...' 형식이다 입력된 영상 정보를 보고 day별로 영상 종합 설명을 해주고 조언을 해줘라"
            }
        ],
        model="gpt-4",
    )
    return chat_completion.choices[0].message.content

def main():
    st.title('유튜브 동영상 관리 및 운동 계획 생성기')

    user_id = st.text_input('사용자 ID를 입력하세요')

    if user_id:
        if 'videos' not in st.session_state:
            st.session_state.videos = get_videos_by_user(user_id, CSV_FILENAME)

        if st.session_state.videos:
            st.subheader(f'{user_id}의 동영상 리스트')

            all_categories = sorted({category for video in st.session_state.videos for category in video['categories']})
            selected_categories = st.multiselect('카테고리를 선택하세요', all_categories, default=all_categories)

            filtered_videos = [video for video in st.session_state.videos if any(category in selected_categories for category in video['categories'])]

            for i, video in enumerate(filtered_videos):
                if i % 3 == 0:
                    cols = st.columns(3)

                video_id = video['video_id']
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                video_title = video['title']
                video_url = video['url']
                video_category = video['category']
                video_length = format_time(video['length'])

                with cols[i % 3]:
                    st.image(thumbnail_url, use_column_width=True)
                    st.caption(f"[{video_title}]({video_url})")
                    st.write(f"{video_length} | {video_category}")


        else:
            st.warning('동영상이 없어요. 추가하세요!')

        st.write('---')
        st.subheader('동영상 추가')

        playlist_url = st.text_input('유튜브 재생목록 URL 입력')

        if st.button('저장하기'):
            if playlist_url == '':
                st.error('재생목록 URL을 입력해주세요.')
            else:
                try:
                    playlist = Playlist(playlist_url)

                    if not os.path.exists(CSV_FILENAME):
                        with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=['user_id', 'video_id', 'title', 'url', 'length', 'author', 'channel_url', 'views', 'category'])
                            writer.writeheader()

                    new_videos_count = 0

                    with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=['user_id', 'video_id', 'title', 'url', 'length', 'author', 'channel_url', 'views', 'category'])

                        for video in playlist.videos:
                            if not is_duplicate(video.video_id, CSV_FILENAME):
                                categorized_video = categorize_video(video.title)
                                video_data = {
                                    'user_id': user_id,
                                    'video_id': video.video_id,
                                    'title': video.title,
                                    'url': video.watch_url,
                                    'length': video.length,
                                    'author': video.author,
                                    'channel_url': video.channel_url,
                                    'views': video.views,
                                    'category': categorized_video.replace("'", "")
                                }
                                writer.writerow(video_data)
                                video_data['categories'] = categorized_video.split(',')
                                st.session_state.videos.append(video_data)
                                new_videos_count += 1

                    if new_videos_count > 0:
                        st.success(f'{new_videos_count}개의 새로운 동영상 정보를 저장했습니다.')
                    else:
                        st.warning('새로 저장된 동영상이 없습니다.')
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f'오류 발생: {str(e)}')

        st.write('---')
        st.subheader('운동 계획 생성')

        videos = load_videos(CSV_FILENAME, user_id)

        if videos.empty:
            st.warning('해당 사용자 ID의 동영상이 없습니다.')
            return

        all_categories = sorted({category for categories in videos['categories'] for category in categories})
        user_categories = st.multiselect('카테고리를 선택하세요', all_categories)
        daily_duration = st.number_input('하루 운동 시간 (분)', min_value=1, value=30)
        num_days = st.number_input('운동 기간 (일)', min_value=1, value=7)

        if st.button('운동 계획 생성'):
            if not user_categories:
                st.error('적어도 하나의 카테고리를 선택해주세요.')
            else:
                filtered_videos = videos[videos['categories'].apply(lambda x: any(category in user_categories for category in x))]

                if filtered_videos.empty:
                    st.warning('선택한 카테고리의 동영상이 없습니다.')
                else:
                    daily_duration_seconds = daily_duration * 60
                    min_daily_duration = daily_duration_seconds - 600
                    max_daily_duration = daily_duration_seconds + 600

                    total_time_seconds = daily_duration_seconds * num_days

                    all_videos = []
                    video_index = 0
                    num_videos = len(filtered_videos)
                    day_outputs = []

                    for day in range(1, num_days + 1):
                        selected_videos = []
                        accumulated_time = 0

                        while accumulated_time < min_daily_duration or (accumulated_time < max_daily_duration and accumulated_time + filtered_videos.iloc[video_index]['length'] <= max_daily_duration):
                            video = filtered_videos.iloc[video_index]
                            selected_videos.append(video)
                            accumulated_time += video['length']
                            video_index = (video_index + 1) % num_videos

                        all_videos.append((day, selected_videos))

                        
                        day_output = (
                            f"Day {day}\n" + 
                            "\n".join([f"{video['title']} ({video['length'] // 60}분) - {video['category']}" for video in selected_videos])
                        )
                        day_outputs.append(day_output)

                    st.success(f'총 {total_time_seconds // 60}분의 운동 계획이 생성되었습니다.')
                    # for day, videos in all_videos:
                    #     st.subheader(f'Day {day}')
                    #     for video in videos:
                    #         st.write(f"{video['title']} ({video['length'] // 60} 분)")
                    #         st.write(f"[동영상 링크]({video['url']})")

                    # CSS 스타일 정의
                    # CSS 스타일 정의
                    # CSS 스타일 정의
                    # CSS 스타일 정의
                    # 동영상 리스트 출력
                    for day, videos in all_videos:
                        st.subheader(f'Day {day}')
                        for i, video in enumerate(videos):
                            if i % 3 == 0:
                                cols = st.columns(3)

                            video_id = video['video_id']
                            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                            video_title = video['title']
                            video_url = video['url']
                            # video_category = video['category']
                            video_length = format_time(video['length'])

                            with cols[i % 3]:
                                st.image(thumbnail_url, use_column_width=True)
                                st.caption(f"[{video_title}]({video_url})")
                                st.write(f"{video_length}")

                    output_string = ",".join(day_outputs)

                    # AI 아이콘 이미지 불러오기
                    ai_icon = Image.open('img.png')  # 'ai_icon.png'는 AI 아이콘 이미지 파일의 경로입니다.

                    # AI 아이콘 출력
                    st.image(ai_icon, width=100)
                    with st.spinner('나는 당신의 운동비서 플랜을 분석 중이니 잠시만 기다려 주세요'):
                      abc = AL_video(output_string)
                    
                    st.markdown("""
                    <div style="border: 2px solid pink; padding: 10px; border-radius: 10px;">
                        <p>안녕하세요, AI 비서입니다.</p>
                        <p>아래는 제가 분석한 홈트 일정입니다:</p>
                        <p style="font-weight: bold;">{}</p>
                    </div>
                    """.format(abc), unsafe_allow_html=True)

if __name__ == '__main__':
    main()

                           
