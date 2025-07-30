# app.py  ──────────────────────────────────────────────
"""
Streamlit WordCloud App
- packages.txt에 'fonts-nanum' 라이브러리를 설치한다는 가정
- 프로젝트 내에 별도 TTF를 올리지 않아도 자동으로 시스템 글꼴(NanumGothic 등)을 찾음
"""
import io, sys, hashlib, urllib.request, matplotlib as mpl
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st
from wordcloud import WordCloud

# ─────────────────────────────────────────────────────
# 1. 한글 글꼴 경로 탐색: 시스템·컨테이너 패키지 우선
# ─────────────────────────────────────────────────────
def get_korean_font() -> str | None:
    """사용 가능한 한글 글꼴 파일(TTF/TTC) 경로를 반환 (없으면 None)."""
    # 1) Debian/Ubuntu fonts-nanum 또는 Noto CJK 패키지 경로
    linux_candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    # 2) macOS 기본 글꼴
    mac_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

    # 3) 프로젝트 내부 fonts/ 폴더(옵션)
    local_font = Path(__file__).parent / "fonts" / "NanumGothic.ttf"
    priority_paths = (*linux_candidates, mac_path, str(local_font))

    for p in priority_paths:
        if Path(p).exists():
            return str(p)
    return None

FONT_PATH = get_korean_font()

# (옵션) 시스템에 글꼴이 없다면 런타임으로 NanumGothic 다운로드 & 캐싱
if FONT_PATH is None:
    CACHE_DIR = Path.home() / ".cache" / "streamlit_fonts"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    url = "https://github.com/naver/nanumfont/raw/master/ttf/NanumGothic.ttf"
    fname = hashlib.md5(url.encode()).hexdigest() + ".ttf"
    FONT_PATH = str(CACHE_DIR / fname)
    if not Path(FONT_PATH).exists():  # 첫 실행 시만 다운로드
        urllib.request.urlretrieve(url, FONT_PATH)

# Matplotlib에도 동일 글꼴 적용
mpl.rcParams["font.family"] = Path(FONT_PATH).stem.split(".")[0]

# ─────────────────────────────────────────────────────
# 2. Streamlit UI
# ─────────────────────────────────────────────────────
st.set_page_config(page_title="실시간 워드클라우드", layout="centered")
st.title("🎈 실시간 워드클라우드 생성기")

user_text = st.text_area("텍스트 입력", height=200)

if st.button("워드클라우드 생성") and user_text.strip():
    wc = WordCloud(
        font_path=FONT_PATH,
        width=800,
        height=400,
        background_color="white",
        max_words=200,
        random_state=42,
    ).generate(user_text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # 다운로드 버튼
    buf = io.BytesIO()
    wc.to_image().save(buf, format="PNG")
    st.download_button(
        label="📥 PNG로 다운로드",
        data=buf.getvalue(),
        file_name="wordcloud.png",
        mime="image/png",
    )
