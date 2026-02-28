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

# 2. 디자인 설정 (이미지 스타일 복원 및 2단 헤더 구현)
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; }
    
    /* 2단 헤더 테이블 디자인 (실종된 제목 셀 복구) */
    .header-table { width: 100%; border-collapse: collapse; margin-bottom: 0px; table-layout: fixed; }
    .header-table th { color: white; border: 1px solid #dee2e6; padding: 12px; text-align: center; font-weight: bold; }
    .bg-past { background-color: #2D6A4F !important; }
    .bg-current { background-color: #D69E2E !important; }
    .bg-future { background-color: #4A5568 !important; }

    /* 입력 위젯 및 자동계산 박스 정렬 */
    div[data-testid="stNumberInput"] label { display: none !important; }
    .auto-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; height: 44px; display: flex; 
                align-items: center; justify-content: center; font-weight: bold; color: #4A5568; border-radius: 4px; }

    /* 결과 표 스타일 (이미지 83747b 스타일 복원) */
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    tbody tr td { text-align: center !important; }
    thead tr th:first-child, tbody tr th { display: none; }

    /* 주석 박스 스타일 (이미지 835713 스타일) */
    .note-container { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 25px; margin-top: 20px; }
    .note-title { font-weight: bold; color: #2D3748; margin-bottom: 10px; display: block; }
    .step-label { font-weight: bold; width: 80px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 중장기 성과지표 목표설정 및 한계점 분석기")

# 사이드바
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 및 중장기 전망 입력")

# 3. [요청반영] 2단 헤더 제목 셀 구현
st.markdown("""
<table class="header-table">
    <tr>
        <th colspan="5" class="bg-past">과거 5개년 실적</th>
        <th rowspan="2" class="bg-current">2026년 (예상) 실적</th>
        <th colspan="3" class="bg-future">중장기 실적 전망</th>
    </tr>
    <tr>
        <th class="bg-past">2021</th><th class="bg-past">2022</th><th class="bg-past">2023</th>
        <th class="bg-past">2024</th><th class="bg-past">2025</th>
        <th class="bg-future">2027</th><th class="bg-future">2028</th><th class="bg-future">2029</th>
    </tr>
</table>
""", unsafe_allow_html=True)

# 한 줄 입력 및 계산
실적_리스트 = []
cols = st.columns(9)

for i in range(5):
    with cols[i]:
        val = st.number_input(f"p_{i}", value=100.0 + (i*5), format="%.3f", key=f"in_{i}")
        실적_리스트.append(val)

with cols[5]:
    예상_2026 = st.number_input("c_2026", value=실적_리스트[-1] * 1.05, format="%.3f", key="in_2026")

# 추세선 기반 자동 계산
X = np.arange(6)
Y = np.array(실적_리스트 + [예상_2026])
slope, intercept = np.polyfit(X, Y, 1)

미래_전망 = []
for i in range(3):
    f_val = slope * (6 + i) + intercept
    미래_전망.append(f_val)
    with cols[6+i]:
        st.markdown(f'<div class="auto-box">{f_val:.3f}</div>', unsafe_allow_html=True)

# 4. [요청반영] 통계 결과 주석화
avg3, std3 = np.mean(실적_리스트[-3:]), np.std(실적_리스트[-3:])
avg5, std5 = np.mean(실적_리스트), np.std(실적_리스트)
avg_f = np.mean(미래_전망)

st.markdown(f"""
<div class="note-container">
    <span class="note-title">📑 실적 분석 참고내용</span>
    • <b>과거 3개년 실적 분석결과:</b> 평균 {avg3:.3f}, 표준편차 {std3:.3f}, 연평균 증가율 {((실적_리스트[-1]/실적_리스트[-3])**(1/2)-1)*100:.2f}%<br>
    • <b>과거 5개년 실적 분석결과:</b> 평균 {avg5:.3f}, 표준편차 {std5:.3f}, 연평균 증가율 {((실적_리스트[-1]/실적_리스트[0])**(1/4)-1)*100:.2f}%<br>
    • <b>중장기 전망 분석결과:</b> 평균 {avg_f:.3f}, 연평균 증가율 {((미래_전망[-1]/예상_2026)**(1/3)-1)*100:.2f}%
</div>
""", unsafe_allow_html=True)

# 5. 분석 실행
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
    오차 = max(np.std(Y), 기준치 * 0.1)
    
    for 명칭, 최고 in 방법별:
        최저 = 기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상_2026 - 최저) / (최고 - 최저))))
        zp = (최고 - 예상_2026) / 오차 if 지표방향=="상향" else (예상_2026 - 최고) / 오차
        도전성_지수 = (zp / 2.0) * 100
        단계 = "🏆 한계 혁신" if 도전성_지수 >= 150 else "🔥 적극 상향" if 도전성_지수 >= 80 else "📈 소극 개선" if 도전성_지수 >= 40 else "⚖️ 현상 유지"
        판정 = "⚠️ 한계" if (abs(최고 - 기준치) > (3 * std3) or abs(최고/기준치 - 1) > 0.3) else "✅ 유지"
        
        결과_데이터.append({
            "평가방법": 명칭, "지표성격": 지표방향, "기준치": 기준치, "최저목표": 최저, "최고목표": 최고,
            "예상실적": 예상_2026, "예상평점": 평점, "가중치": 가중치_값, "예상득점": 평점 * (가중치_값 / 100.0), 
            "도전성 단계": 단계, "추세치 분석결과": 판정
        })

    st.subheader("2. 평가방법별 비교 분석 결과 및 임계점 진단")
    df_res = pd.DataFrame(결과_데이터)
    st.table(df_res.style.format({col: "{:.3f}" for col in df_res.columns if col not in ["평가방법", "지표성격", "도전성 단계", "추세치 분석결과", "예상평점"]}).format({"예상평점": "{:.2f}"}))

    # [요청반영] 도전성 단계 주석 복구
    st.markdown("""
    <div class="note-container">
        <span class="note-title">1. 도전성 단계 분석 (과거 추세 대비 상향 정도)</span>
        • <span class="step-label">🏆 한계 혁신</span>: 과거의 흐름을 완전히 벗어난 파격적 목표로, 조직 역량의 대전환이 필요한 수준입니다.<br>
        • <span class="step-label">🔥 적극 상향</span>: 과거 성장세를 상회하는 공격적 목표로, 성과 창출을 위한 적극적 노력이 수반됩니다.<br>
        • <span class="step-label">📈 소극 개선</span>: 과거의 완만한 우상향 추세를 따르는 수준으로, 통상적인 노력으로 달성 가능합니다.<br>
        • <span class="step-label">⚖️ 현상 유지</span>: 과거 실적 평균 수준의 목표로, 도전성보다는 안정적 관리에 치중한 상태입니다.
    </div>
    """, unsafe_allow_html=True)

    # 그래프 시각화
    st.subheader("3. 2029년 중장기 전망 및 목표 수준 시뮬레이션")
    fig, ax = plt.subplots(figsize=(11, 5))
    연도_축 = [f"'{y-2000}" for y in range(2021, 2030)]
    
    ax.plot(연도_축, slope * np.arange(9) + intercept, color='#CBD5E0', linestyle='--', label='중장기 추세선')
    ax.plot(연도_축[:5], Y[:5], marker='o', color='#2D3748', linewidth=2.5, label='과거 실적')
    ax.scatter(연도_축[5], 예상_2026, color='#E53E3E', s=200, marker='D', zorder=10, label='2026 예상')
    
    for i, row in df_res.iterrows():
        ax.scatter(연도_축[5], row['최고목표'], s=120, edgecolors='black', label=f"{row['평가방법']}")

    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)
    plt.subplots_adjust(right=0.75)
    st.pyplot(fig)
