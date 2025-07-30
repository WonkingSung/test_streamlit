import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ------------------- 한글 폰트 설정 -------------------
plt.rcParams['font.family'] = 'Apple SD Gothic Neo'  # Mac
# plt.rcParams['font.family'] = 'Malgun Gothic'      # Windows
plt.rcParams['axes.unicode_minus'] = False

# ------------------- 데이터 불러오기 -------------------
file_path = "data.csv"
df = pd.read_csv(file_path, encoding='cp949')

# 연도별 인구 컬럼만 추출
population_cols = [col for col in df.columns if "거주자 인구수" in col]

# NaN 안전하게 정수 변환
df_numeric = df.copy()
for col in population_cols:
    df_numeric[col] = (
        df_numeric[col]
        .astype(str)
        .str.replace(",", "")
        .replace("nan", "0")
        .replace("", "0")
        .astype(float)
        .astype(int)
    )

# ------------------- Streamlit UI -------------------
st.title("📊 주민등록 인구 및 세대 현황 (2015~2024)")

tab1, tab2, tab3 = st.tabs(
    ["📈 개별 지역 분석", "🔥 인구 변동 상위 5개 지역", "📊 증가/감소 지역 분석"]
)

# ======================= TAB 1 : 개별 지역 분석 =======================
with tab1:
    region_list = df['행정구역'].unique()
    selected_region = st.selectbox("행정구역 선택", region_list)

    # 선택된 지역 데이터
    region_data = df_numeric[df_numeric['행정구역'] == selected_region]

    # 표 출력
    st.subheader("📋 선택 지역 데이터")
    st.dataframe(df[df['행정구역'] == selected_region])  # 원본 표 (콤마 유지)

    # 연도별 인구 시각화
    population = region_data[population_cols].iloc[0]
    years = [col.split("_")[0] for col in population_cols]

    fig, ax = plt.subplots()
    ax.plot(years, population, marker='o')
    ax.set_xlabel("연도")
    ax.set_ylabel("인구수")
    ax.set_title(f"{selected_region} 연도별 인구 추이")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ======================= TAB 2 : 인구 변동 상위 5개 지역 =======================
with tab2:
    st.subheader("🔥 인구 변동 폭 상위 5개 지역")

    # 변동폭 계산
    df_numeric['인구변동폭'] = df_numeric[population_cols].max(axis=1) - df_numeric[population_cols].min(axis=1)

    # 상위 5개 지역
    top5 = df_numeric.nlargest(5, '인구변동폭')
    top5_names = top5['행정구역'].tolist()
    st.write("**상위 5개 지역:**", ", ".join(top5_names))

    # 연도별 합산 인구
    top5_sum = top5[population_cols].sum()
    years = [col.split("_")[0] for col in population_cols]

    # 합산 그래프
    fig2, ax2 = plt.subplots()
    ax2.plot(years, top5_sum, marker='o', color='red', label='상위 5개 지역 합계')
    ax2.set_xlabel("연도")
    ax2.set_ylabel("총 인구수")
    ax2.set_title("연도별 인구 합계 (상위 5개 변동 지역)")
    ax2.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # 개별 그래프
    fig3, ax3 = plt.subplots()
    for idx, row in top5.iterrows():
        ax3.plot(years, row[population_cols], marker='o', label=row['행정구역'])
    ax3.set_xlabel("연도")
    ax3.set_ylabel("인구수")
    ax3.set_title("상위 5개 변동 지역 연도별 인구 추이")
    ax3.legend(fontsize=8)
    plt.xticks(rotation=45)
    st.pyplot(fig3)

# ======================= TAB 3 : 증가 / 감소 지역 분석 =======================
with tab3:
    st.subheader("📊 2015년 대비 2024년 인구 증감 분석")

    # 2015년 / 2024년 인구
    start_pop = df_numeric[population_cols[0]]
    end_pop = df_numeric[population_cols[-1]]
    df_numeric['증감'] = end_pop - start_pop

    # 상위 5개 증가 / 감소 지역
    top5_increase = df_numeric.nlargest(5, '증감')
    top5_decrease = df_numeric.nsmallest(5, '증감')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📈 인구 증가 상위 5개 지역")
        st.dataframe(top5_increase[['행정구역', '증감']])
    with col2:
        st.markdown("### 📉 인구 감소 상위 5개 지역")
        st.dataframe(top5_decrease[['행정구역', '증감']])

    # 그래프 시각화
    fig4, ax4 = plt.subplots()
    ax4.bar(top5_increase['행정구역'], top5_increase['증감'], color='green', label='증가')
    ax4.bar(top5_decrease['행정구역'], top5_decrease['증감'], color='red', label='감소')
    ax4.set_ylabel("인구 증감수")
    ax4.set_title("상위 5개 증가 / 감소 지역 비교")
    ax4.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig4)
