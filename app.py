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

# 2. CSS 디자인 (가독성 최우선, 이미지 스타일 복원)
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    /* 전체 폰트 및 배경 */
    html, body, [class*="st-"] { font-size: 15px !important; font-family: 'NanumGothic', sans-serif; }
    
    /* 대분류 헤더 스타일 (2단 헤더 대용) */
    .main-header { padding: 10px; color: white; text-align: center; font-weight: bold; margin-bottom: 5px; border-radius: 5px 5px 0 0; }
    .bg-past { background-color: #2D6A4F; }
    .bg-current { background-color: #D69E2E; }
    .bg-future { background-color: #4A5568; }

    /* 개별 연도 헤더 스타일 */
    .sub-header { background-color: #f1f3f5; padding: 5px; text-align: center; font-size: 13px; font-weight: bold; border: 1px solid #dee2e6; border-top: none; }

    /* 입력창 여백 제거 */
    div[data-testid="stNumberInput"] label { display: none !important; }
    div[data-testid="stNumberInput"] > div { margin-top: -1px !important; }

    /* 자동계산 결과창 */
    .auto-res { background-color: #F8FAFC; border: 1px solid #dee2e6; height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }

    /* 분석 지표 가이드 (이미지 835713 스타일) */
    .guide-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; line-height: 1.8; }
    .guide-title { font-weight: bold; color: #2D3748; font-size: 16px; margin-bottom: 10px; display: block; }
    
    /* 결과 테이블 스타일 */
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; }
    thead tr th:first-child, tbody tr th { display: none; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 중장기 성과지표 목표설정 및 한계점 분석기")

# 사이드바
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 및 중장기 전망 입력")

# 3. 레이아웃 구현 (실종된 제목 셀 해결을 위해 컨테이너 방식 채택)
실적_리스트 = []
m_cols = st.columns([5, 1, 3]) # 과거5, 현재1, 미래3 비율

# --- 과거 5개년 섹션 ---
with m_cols[0]:
    st.markdown('<div class="main-header bg-past">과거 5개년 실적 (2021~2025)</div>', unsafe_allow_html=True)
    p_cols = st.columns(5)
    for i, year in enumerate(range(2021, 2026)):
        with p_cols[i]:
            st.markdown(f'<div class="sub-header">{year}</div>', unsafe_allow_html=True)
            val = st.number_input(f"p_{year}", value=100.0 + (i*5), format="%.3f", key=f"v_{year}")
            실적_리스트.append(val)

# --- 2026 예상 섹션 ---
with m_cols[1]:
    st.markdown('<div class="main-header bg-current">2026년 (예상)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">실적 입력</div>', unsafe_allow_html=True)
    예상_2026 = st.number_input("curr_2026", value=실적_리스트[-1] * 1.05, format="%.3f", key="v_2026")

# --- 미래 전망 섹션 (자동계산) ---
with m_cols[2]:
    st.markdown('<div class="main-header bg-future">중장기 실적 전망 (자동)</div>', unsafe_allow_html=True)
    f_cols = st.columns(3)
    
    # 추세 계산 로직
    X = np.arange(6)
    Y = np.array(실적_리스트 + [예상_2026])
    slope, intercept = np.polyfit(X, Y, 1)
    
    미래_전망 = []
    for i, year in enumerate(range(2027, 2030)):
        with f_cols[i]:
            st.markdown(f'<div class="sub-header">{year}</div>', unsafe_allow_html=True)
            f_val = slope * (6 + i) + intercept
            미래_전망.append(f_val)
            st.markdown(f'<div class="auto-res">{f_val:.3f}</div>', unsafe_allow_html=True)

# 4. 실적 분석 참고내용 (이미지 82e9b2 스타일)
avg3, std3 = np.mean(실적_리스트[-3:]), np.std(실적_리스트[-3:])
avg5, std5 = np.mean(실적_리스트), np.std(실적_리스트)
avg_f = np.mean(미래_전망)

st.markdown(f"""
<div class="guide-box">
    <span class="guide-title">📑 실적 분석 참고내용</span>
    • <b>과거 3개년 실적 분석결과:</b> 평균 {avg3:.3f}, 표준편차 {std3:.3f}, 연평균 증가율 {((실적_리스트[-1]/실적_리스트[-3])**(1/2)-1)*100:.2f}%<br>
    • <b>과거 5개년 실적 분석결과:</b> 평균 {avg5:.3f}, 표준편차 {std5:.3f}, 연평균 증가율 {((실적_리스트[-1]/실적_리스트[0])**(1/4)-1)*100:.2f}%<br>
    • <b>중장기 전망 분석결과:</b> 평균 {avg_f:.3f}, 연평균 증가율 {((미래_전망[-1]/예상_2026)**(1/3)-1)*100:.2f}%
</div>
""", unsafe_allow_html=True)

# 5. 분석 실행 및 결과
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

    # 도전성 단계 가이드 복구 (이미지 835713 스타일)
    st.markdown("""
    <div class="guide-box">
        <span class="guide-title">💡 분석 지표 가이드</span>
        <b>1. 도전성 단계 분석 (과거 추세 대비 상향 정도)</b><br>
        • 🏆 <b>한계 혁신</b>: 목표치가 예상 실적보다 표준편차의 3배(<span class="formula">3σ</span>) 이상 높은 경우로, 과거의 흐름을 완전히 벗어난 파격적 목표 수준<br>
        • 🔥 <b>적극 상향</b>: 목표치가 과거 변동폭의 1.6배~3배 수준으로, 과거 성장세를 상회하는 공격적 목표 수준<br>
        • 📈 <b>소극 개선</b>: 목표치가 과거 변동 범위 내에 존재하며, 과거의 완만한 우상향 추세를 따르는 안정적 수준<br>
        • ⚖️ <b>현상 유지</b>: 목표치가 예상 실적과 유사하거나 과거 평균 수준에 머무르는 경우로, 과거 실적 평균 수준의 관리 중심 목표 수준<br><br>
        <b>2. 추세치 분석결과 (한계 판정 기준)</b><br>
        • ⚠️ <b>한계</b>: 목표치가 과거 표준편차의 3배를 초과하거나 30% 이상 급변하여 역량상 임계점에 도달했음을 의미합니다.
    </div>
    """, unsafe_allow_html=True)

    # 그래프 시각화 (NameError 방지를 위해 subplot_adjust 수정)
    st.subheader("3. 2029년 중장기 전망 및 목표 수준 시뮬레이션")
    fig, ax = plt.subplots(figsize=(11, 5))
    연도_축 = [f"'{y-2000}" for y in range(2021, 2030)]
    
    ax.plot(연도_축, slope * np.arange(9) + intercept, color='#CBD5E0', linestyle='--', label='중장기 추세선')
    ax.plot(연도_축[:5], Y[:5], marker='o', color='#2D6A4F', linewidth=2.5, label='과거 실적')
    ax.scatter(연도_축[5], 예상_2026, color='#D69E2E', s=200, marker='D', zorder=10, label='2026 예상')
    
    for i, row in df_res.iterrows():
        ax.scatter(연도_축[5], row['최고목표'], s=120, edgecolors='black', label=f"{row['평가방법']}")

    ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1.0, 1.0))
    st.pyplot(fig)
