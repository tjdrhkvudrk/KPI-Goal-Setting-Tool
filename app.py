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

# 2. 디자인 설정 (15px 통일 및 중장기 열 레이아웃)
st.set_page_config(page_title="중장기 성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    table { width: 100% !important; table-layout: fixed !important; border-collapse: collapse; }
    th { background-color: #4A5568 !important; color: white !important; font-size: 14px !important; font-weight: bold !important; text-align: center !important; border: 1px solid #dee2e6 !important; height: 50px; }
    td { font-size: 14px !important; text-align: center !important; border: 1px solid #dee2e6 !important; background-color: white !important; height: 40px; }
    td:first-child, th:first-child { width: 100px !important; background-color: #EDF2F7 !important; font-weight: bold; }
    .header-box { color: white; padding: 10px; text-align: center; font-weight: bold; font-size: 14px !important; border: 1px solid #dee2e6; min-height: 50px; display: flex; align-items: center; justify-content: center; }
    .highlight-input input { background-color: #FFFBEB !important; font-weight: bold !important; color: #D69E2E !important; }
    .auto-calc { background-color: #F7FAFC !important; color: #4A5568 !important; border: 1px solid #E2E8F0; border-radius: 4px; padding: 10px; text-align: center; font-size: 14px; font-weight: bold; height: 42px; display: flex; align-items: center; justify-content: center; }
    .footer-note { font-size: 12px; color: #718096; margin-top: 5px; line-height: 1.4; }
    .logic-box { background-color: #F8FAFC; padding: 20px; border: 1px solid #E2E8F0; border-radius: 10px; margin-top: 30px; border-left: 5px solid #2D3748; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 중장기 성과지표 목표설정 및 한계점 분석기")

# 3. 데이터 입력 및 자동 계산 (2021~2029)
st.sidebar.header("📍 지표 기본 설정")
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 입력 및 중장기 전망")
실적_리스트 = []
# 2021~2025 실적 입력
cols1 = st.columns(5)
for i in range(5):
    with cols1[i]:
        st.markdown(f'<div class="header-box" style="background-color:#2D6A4F;">{2021+i}년 실적</div>', unsafe_allow_html=True)
        val = st.number_input(f"v_{2021+i}", value=100.0 + (i*5), format="%.3f", label_visibility="collapsed")
        실적_리스트.append(val)

# 2026 예상 실적 입력 및 2027~2029 자동 계산
cols2 = st.columns(4)
with cols2[0]:
    st.markdown('<div class="header-box" style="background-color:#D69E2E;">2026년 예상 실적</div>', unsafe_allow_html=True)
    st.markdown('<div class="highlight-input">', unsafe_allow_html=True)
    예상_2026 = st.number_input("v_2026", value=실적_리스트[-1] * 1.05, format="%.3f", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# 2021~2026 기반 추세 분석 (2027~2029 예측용)
X_base = np.arange(6)
Y_base = np.array(실적_리스트 + [예상_2026])
slope, intercept = np.polyfit(X_base, Y_base, 1)

미래_실적 = []
for i, year in enumerate([2027, 2028, 2029]):
    calc_val = slope * (6 + i) + intercept
    미래_실적.append(calc_val)
    with cols2[i+1]:
        st.markdown(f'<div class="header-box" style="background-color:#4A5568;">{year}년 예상(자동)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="auto-calc">{calc_val:.3f}</div>', unsafe_allow_html=True)

전체_실적 = 실적_리스트 + [예상_2026] + 미래_실적

# 기초 통계 계산 (중장기 연평균 증가율 포함)
평균_3년 = float(np.mean(실적_리스트[-4:-1]))
표준편차_3년 = float(np.std(실적_리스트[-4:-1]))
직전_실적 = float(실적_리스트[-1])
기준치 = float(max(평균_3년, 직전_실적) if 지표방향=="상향" else min(평균_3년, 직전_실적))
중장기_CAGR = ((전체_실적[-1] / 전체_실적[0])**(1/8) - 1) * 100 if 전체_실적[0] != 0 else 0

stats_df = pd.DataFrame({
    "과거 3개년 평균": [평균_3년], "과거 3개년 표준편차": [표준편차_3년], 
    "직전년도 실적": [직전_실적], "중장기 연평균 증가율 예상치(%)": [중장기_CAGR]
}, index=["구분"])
st.table(stats_df.style.format("{:.3f}"))

# 4. 분석 실행 및 한계점 판정
st.markdown("---")
if st.button("🚀 중장기 성과 및 한계점 분석 실행"):
    방법별 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차_3년 if 지표방향=="상향" else 기준치 - 2*표준편차_3년, "#1abc9c"),
        ("목표부여(1편차)", 기준치 + 표준편차_3년 if 지표방향=="상향" else 기준치 - 표준편차_3년, "#3498db"),
        ("목표부여(120%)", 기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8, "#9b59b6"),
        ("목표부여(110%)", 기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9, "#f39c12")
    ]

    결과_데이터 = []
    for 명칭, 최고, 색상 in 방법별:
        최저 = 기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상_2026 - 최저) / (최고 - 최저))))
        
        # [요청 반영] 한계점 판정 로직
        # 기준: 목표치가 과거 3개년 표준편차의 3배를 초과하거나, 과거 최고점 대비 30% 이상 상향 시 '한계'
        diff = abs(최고 - 기준치)
        if diff > (3 * 표준편차_3년) or (abs(최고/기준치 - 1) > 0.3):
            판정 = "⚠️ 한계"
        else:
            판정 = "✅ 유지"
            
        결과_데이터.append({
            "평가방법": 명칭, "지표성격": 지표방향, "기준치": 기준치, "최저목표": 최저, "최고목표": 최고,
            "예상평점": 평점, "가중치": 가중치_값, "예상득점": 평점 * (가중치_값 / 100.0), "추세치 분석결과": 판정
        })

    st.subheader("2. 평가방법별 비교 분석 결과 및 임계점 진단")
    df_res = pd.DataFrame(결과_데이터)
    df_res.index = [f"{i+1}" for i in range(len(df_res))]
    df_res.index.name = "구분"
    st.table(df_res.style.format({
        "기준치": "{:.3f}", "최저목표": "{:.3f}", "최고목표": "{:.3f}", 
        "예상평점": "{:.2f}", "가중치": "{:.3f}", "예상득점": "{:.3f}"
    }))
    
    # [요청 반영] 한계 판정 주석
    st.markdown("""
    <div class="footer-note">
        ※ <b>추세치 분석결과 주석:</b><br>
        - <b>한계:</b> 설정된 최고목표가 과거 실적 변동성(표준편차)의 3배를 초과하거나 기준치 대비 30% 이상의 급격한 상향이 필요한 지점입니다. 
        이는 조직의 역량이 임계점에 도달했음을 의미하며, 추가적인 목표 상향 시 달성 가능성이 현저히 낮아질 수 있음을 시사합니다.<br>
        - <b>유지:</b> 현재의 개선 속도와 자원 투입으로 충분히 관리 및 달성이 가능한 도전적 범위 내의 목표입니다.
    </div>
    """, unsafe_allow_html=True)

    # 3. 시각화 (2029년까지 확대)
    st.subheader("3. 2029년 중장기 전망 및 목표 수준")
    fig, ax = plt.subplots(figsize=(11, 5))
    연도_축 = [f"'{y-2000}" for y in range(2021, 2030)]
    
    # 추세선 및 실적 표시
    ax.plot(연도_축, slope * np.arange(9) + intercept, color='#CBD5E0', linestyle='--', label='중장기 추세선')
    ax.plot(연도_축[:5], 전체_실적[:5], marker='o', color='#2D3748', linewidth=2.5, label='과거 실적')
    ax.scatter(연도_축[5], 예상_2026, color='#E53E3E', s=200, marker='D', zorder=10, label='2026 예상')
    ax.plot(연도_축[5:], 전체_실적[5:], marker='s', color='#718096', alpha=0.5, label='미래 전망')
    
    # 목표선 표시
    for i, row in df_res.iterrows():
        ax.scatter(연도_축[5], row['최고목표'], s=120, edgecolors='black', label=f"{row['평가방법']} ({row['최고목표']:.2f})")

    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)
    plt.subplots_adjust(right=0.75)
    st.pyplot(fig)

    # 최종 논리 근거
    st.markdown('<div class="logic-box">', unsafe_allow_html=True)
    st.subheader("💡 성과관리 전략 제언")
    best = df_res.loc[df_res['예상득점'].idxmax()]
    st.write(f"2029년까지의 중장기 연평균 증가율 예상치는 **{중장기_CAGR:.3f}%**로 분석되었습니다.")
    st.write(f"현재 2026년 목표 설정 시 **{best['평가방법']}**을 적용할 경우, 분석 결과는 **'{best['추세치 분석결과']}'** 상태입니다. 이는 중장기 추세와 조직의 임계점을 고려했을 때 가장 전략적인 선택지가 될 것입니다.")
    st.markdown('</div>', unsafe_allow_html=True)
