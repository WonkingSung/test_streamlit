import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 주민등록 인구 및 세대 현황 (2015~2024)")

@st.cache_data
def load_data():
    file_path = "201512_202412_주민등록인구및세대현황_연간 (1).csv"
    # UTF-8-SIG 기본, 실패 시 CP949
    try:
        return pd.read_csv(file_path, encoding='utf-8-sig')
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding='cp949')

df = load_data()

# 인구수 컬럼 추출
population_cols = [col for col in df.columns if "거주자 인구수" in col]

# 정수 변환
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

# 탭 구성
tab1, tab2, tab3 = st.tabs(
    ["📈 개별 지역 분석", "🔥 인구 변동 상위 5개 지역", "📊 증가/감소 지역 분석"]
)

# =================== TAB 1 : 개별 지역 ===================
with tab1:
    region_list = df['행정구역'].unique()
    selected_region = st.selectbox("행정구역 선택", region_list)
    
    region_data = df_numeric[df_numeric['행정구역'] == selected_region]
    st.dataframe(df[df['행정구역'] == selected_region])

    population = region_data[population_cols].iloc[0]
    years = [col.split("_")[0] for col in population_cols]

    fig = px.line(
        x=years, y=population,
        markers=True,
        labels={"x":"연도","y":"인구수"},
        title=f"{selected_region} 연도별 인구 추이"
    )
    st.plotly_chart(fig, use_container_width=True)

# =================== TAB 2 : 인구 변동 상위 5개 지역 ===================
with tab2:
    st.subheader("🔥 인구 변동 폭 상위 5개 지역")
    df_numeric['인구변동폭'] = df_numeric[population_cols].max(axis=1) - df_numeric[population_cols].min(axis=1)
    top5 = df_numeric.nlargest(5, '인구변동폭')

    st.write("**상위 5개 지역:**", ", ".join(top5['행정구역'].tolist()))

    # 개별 지역 추이
    melted = top5.melt(id_vars='행정구역', value_vars=population_cols,
                       var_name='연도', value_name='인구수')
    melted['연도'] = melted['연도'].str.split("_").str[0]

    fig2 = px.line(
        melted, x='연도', y='인구수', color='행정구역', markers=True,
        title="상위 5개 지역 연도별 인구 추이"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 5개 지역 합계
    top5_sum = top5[population_cols].sum().reset_index()
    top5_sum.columns = ['연도', '총인구']
    top5_sum['연도'] = top5_sum['연도'].str.split("_").str[0]

    fig3 = px.line(
        top5_sum, x='연도', y='총인구', markers=True,
        title="상위 5개 지역 인구 합계 추이"
    )
    st.plotly_chart(fig3, use_container_width=True)

# =================== TAB 3 : 증가/감소 분석 ===================
with tab3:
    start_pop = df_numeric[population_cols[0]]
    end_pop = df_numeric[population_cols[-1]]
    df_numeric['증감'] = end_pop - start_pop

    top5_increase = df_numeric.nlargest(5, '증감')[['행정구역','증감']]
    top5_decrease = df_numeric.nsmallest(5, '증감')[['행정구역','증감']]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📈 인구 증가 상위 5개 지역")
        st.dataframe(top5_increase)
    with col2:
        st.markdown("### 📉 인구 감소 상위 5개 지역")
        st.dataframe(top5_decrease)

    # Plotly 막대그래프
    inc_fig = px.bar(top5_increase, x='행정구역', y='증감', color='행정구역',
                     title="인구 증가 상위 5개 지역")
    dec_fig = px.bar(top5_decrease, x='행정구역', y='증감', color='행정구역',
                     title="인구 감소 상위 5개 지역")

    st.plotly_chart(inc_fig, use_container_width=True)
    st.plotly_chart(dec_fig, use_container_width=True)
