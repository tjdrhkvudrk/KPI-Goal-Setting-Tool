import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 설정
@st.cache_resource
def load_korean_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
    font_path = "NanumGothic-Bold.ttf"
    if not os.path.exists(font_path):
        try:
            res = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(res.content)
        except: pass
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
    plt.rc('axes', unicode_minus=False)
    return font_path

font_file = load_korean_font()
font_prop = fm.FontProperties(fname=font_file) if font_file else None

# 2. 디자인 설정 (2단 헤더 구조 최적화)
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; }
    
    /* 2단 헤더 테이블 디자인 */
    .custom-table { width: 100%; border-collapse: collapse; margin-bottom: 0px; table-layout: fixed; }
    .custom-table th { background-color: #4A5568; color: white; border: 1px solid #dee2e6; padding: 10px; text-align: center; font-weight: bold; }
    .header-past { background-color: #2D6A4F !important; }
    .header-current { background-color: #D69E2E !important; }
    .header-future { background-color: #4A5568 !important; }

    /* 입력 필드 스타일 조정 */
    div[data-testid="stNumberInput"] { margin: 0px !important; padding: 0px !important; }
    div[data-testid="stNumberInput"] label { display: none !important; }
    
    /* 자동계산 결과 박스 */
    .calc-res { background-color: #F8FAFC; border: 1px solid #E2E8F0; height: 45px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #4A5568; border-radius: 4px; }

    /* 하단 주석 박스 */
    .footer-note { font-size: 14px; color: #4A5568; margin-top: 15px; line-height: 1.8; padding: 20px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; }
    
    /* 결과 표 스타일 */
    thead tr th:first-child, tbody tr th { display: none; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 중장기 성과지표 목표설정 및 한계점 분석기")

# 사이드바 설정
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 및 중장기 전망 입력")

# 3. 2단 헤더 테이블 시각적 구현
st.markdown("""
<table class="custom-table">
    <tr>
        <th colspan="5" class="header-past">과거 5개년 실적</th>
        <th rowspan="2" class="header-current">2026년 (예상) 실적</th>
        <th colspan="3" class="header-future">중장기 실적 전망</th>
    </tr>
    <tr>
        <th class="header-past">2021</th><th class="header-past">2022</th><th class="header-past">2023</th>
        <th class="header-past">2024</th><th class="header-past">2025</th>
        <th class="header-future">2027</th><th class="header-future">2028</th><th class="header-future">2029</th>
    </tr>
</table>
""", unsafe_allow_html=True)

# 실제 입력 위젯 한 줄 배치
실적_리스트 = []
input_cols = st.columns(9)

for i in range(5):
    with input_cols[i]:
        val = st.number_input(f"past_{2021+i}", value=100.0 + (i*5), format="%.3f")
        실적_리스트.append(val)

with input_cols[5]:
    예상_2026 = st.number_input("current_2026", value=실적_리스트[-1] * 1.05, format="%.3f")

# 추세 계산 로직
X_base = np.arange(6)
Y_base = np.array(실적_리스트 + [예상_2026])
slope, intercept = np.polyfit(X_base, Y_base, 1)

미래_실적 = []
for i in range(3):
    calc_val = slope * (6 + i) + intercept
    미래_실적.append(calc_val)
    with input_cols[6+i]:
        st.markdown(f'<div class="calc-res">{calc_val:.3f}</div>', unsafe_allow_html=True)

# 4. 하단 참고 내용 (주석 처리)
avg3, std3 = np.mean(실적_리스트[-3:]), np.std(실적_리스트[-3:])
avg5, std5 = np.mean(실적_리스트), np.std(실적_리스트)
avg_f, std_f = np.mean(미래_실적), np.std(미래_실적)

st.markdown(f"""
<div class="footer-note">
    <b>📋 실적 분석 참고내용</b><br>
    * <b>과거 3개년 실적 분석결과:</b> 평균 {avg3:.3f}, 표준편차 {std3:.3f}, 연평균 증가율 {((실적_리스트[-1]/실적_리스트[-3])**(1/2)-1)*100:.2f}%<br>
    * <b>과거 5개년 실적 분석결과:</b> 평균 {avg5:.3f}, 표준편차 {std5:.3f}, 연평균 증가율 {((실적_리스트[-1]/실적_리스트[0])**(1/4)-1)*100:.2f}%<br>
    * <b>중장기 전망 분석결과:</b> 평균 {avg_f:.3f}, 표준편차 {std_f:.3f}, 연평균 증가율 {((미래_실적[-1]/예상_2026)**(1/3)-1)*100:.2f}%
</div>
""", unsafe_allow_html=True)

# 5. 분석 실행 및 결과 테이블
st.markdown("---")
if st.button("🚀 중장기 성과 및 한계점 분석 실행"):
    기준치 = float(max(avg3, 실적_리스트[-1]) if 지표방향=="상향" else min(avg3, 실적_리스트[-1]))
    방법별 = [
        ("목표부여(2편차)", 기준치 + 2*std3 if 지표방향=="상향" else 기준치 - 2*std3),
        ("목표부여(1편차)", 기준치 + std3 if 지표방향=="상향" else 기준치 - std3),
        ("목표부여(120%)", 기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8),
        ("목표부여(110%)", 기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9)
    ]

    결과_데이터 = []
    오차 = max(np.std(Y_base), 기준치 * 0.1)
    
    for 명칭, 최고 in 방법별:
        최저 = 기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상_2026 - 최저) / (최고 - 최저))))
        
        # 도전성 지수 계산
        zp = (최고 - 예상_2026) / 오차 if 지표방향=="상향" else (예상_2026 - 최고) / 오차
        도전성_지수 = (zp / 2.0) * 100
        단계 = "🏆 한계 혁신" if 도전성_지수 >= 150 else "🔥 적극 상향" if 도전성_지수 >= 80 else "📈 소극 개선" if 도전성_지수 >= 40 else "⚖️ 현상 유지"
        
        # 한계점 판정
        판정 = "⚠️ 한계" if (abs(최고 - 기준치) > (3 * std3) or abs(최고/기준치 - 1) > 0.3) else "✅ 유지"
        
        결과_데이터.append({
            "평가방법": 명칭, "지표성격": 지표방향, "기준치": 기준치, "최저목표": 최저, "최고목표": 최고,
            "예상실적": 예상_2026, "예상평점": 평점, "가중치": 가중치_값, "예상득점": 평점 * (가중치_값 / 100.0), 
            "도전성 단계": 단계, "추세치 분석결과": 판정
        })

    st.subheader("2. 평가방법별 비교 분석 결과 및 임계점 진단")
    df_res = pd.DataFrame(결과_데이터)
    display_cols = ["평가방법", "지표성격", "기준치", "최저목표", "최고목표", "예상실적", "예상평점", "가중치", "예상득점", "도전성 단계", "추세치 분석결과"]
    st.table(df_res[display_cols].style.format({
        "기준치": "{:.3f}", "최저목표": "{:.3f}", "최고목표": "{:.3f}", "예상실적": "{:.3f}",
        "예상평점": "{:.2f}", "가중치": "{:.3f}", "예상득점": "{:.3f}"
    }))

    # 그래프 시각화
    st.subheader("3. 2029년 중장기 전망 및 목표 수준 시뮬레이션")
    fig, ax = plt.subplots(figsize=(11, 5))
    연도_축 = [f"'{y-2000}" for y in range(2021, 2030)]
    전체_실적 = 실적_리스트 + [예상_2026] + 미래_실적
    
    ax.plot(연도_축, slope * np.arange(9) + intercept, color='#CBD5E0', linestyle='--', label='중장기 추세선')
    ax.plot(연도_축[:5], 전체_실적[:5], marker='o', color='#2D3748', linewidth=2.5, label='과거 실적')
    ax.scatter(연도_축[5], 예상_2026, color='#E53E3E', s=200, marker='D', zorder=10, label='2026 예상')
    ax.plot(연도_축[5:], 전체_실적[5:], marker='s', color='#718096', alpha=0.5, label='미래 전망')
    
    for i, row in df_res.iterrows():
        ax.scatter(연도_축[5], row['최고목표'], s=120, edgecolors='black', label=f"{row['평가방법']}")

    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)
    plt.subplots_adjust(right=0.75)
    st.pyplot(fig)
