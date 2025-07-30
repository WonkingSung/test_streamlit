# streamlit_wordcloud_app_mac.py
import io, matplotlib as mpl
from pathlib import Path
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ------------ macOS 전용 한글 폰트 설정 ------------
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
mpl.rcParams['font.family'] = 'Apple SD Gothic Neo'   # Matplotlib 그래프용

# ------------ Streamlit UI (기존과 동일) ------------
st.title("🎈 실시간 워드클라우드 생성기 (macOS)")
user_text = st.text_area("텍스트 입력", height=200)
if st.button("워드클라우드 생성") and user_text.strip():
    wc = WordCloud(
        font_path=FONT_PATH,          # ✅ 여기만 지정
        width=800, height=400, background_color="white"
    ).generate(user_text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
    st.pyplot(fig)