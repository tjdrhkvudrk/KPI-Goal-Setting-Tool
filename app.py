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
            with open(font_path, "wb") as f: f.write(res.content)
        except: pass
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
    plt.rc('axes', unicode_minus=False)
    return font_path

font_file = load_korean_font()
font_prop = fm.FontProperties(fname=font_file) if font_file else None

# 2. CSS 디자인 (가이드 가독성 극대화)
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; font-family: 'NanumGothic', sans-serif; }
    .main-header { padding: 10px; color: white; text-align: center; font-weight: bold; margin-bottom: 5px; border-radius: 5px 5px 0 0; }
    .bg-past { background-color: #2D6A4F; }
    .bg-current { background-color: #D69E2E; }
    .bg-future { background-color: #4A5568; }
    .sub-header { background-color: #f1f3f5; padding: 5px; text-align: center; font-size: 13px; font-weight: bold; border: 1px solid #dee2e6; border-top: none; }
    .sb-title { font-size: 16px !important; font-weight: 800 !important; color: #1A202C; margin-top: 15px; margin-bottom: 5px; display: block; }
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label, div[data-testid="stRadio"] > label { display: none !important; }
    .auto-res { background-color: #F8FAFC; border: 1px solid #dee2e6; height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .guide-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; line-height: 1.8; }
    .recom-box { background-color: #F0F4F8; border: 1px solid #2B6CB0; border-radius: 10px; padding: 20px; margin-top: 15px; border-left: 8px solid #2B6CB0; }
    .logic-box { background-color: #FFFFFF; border: 1px solid #CBD5E0; border-radius: 8px; padding: 15px; margin-top: 10px; }
    .guide-title { font-weight: bold; color: #2D3748; font-size: 16px; margin-bottom: 10px; display: block; }
    .point-txt { color: #C53030; font-weight: bold; }
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; }
    thead tr th:first-child, tbody tr th { display: none; }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바 설정
with st.sidebar:
    st.markdown('<p class="sb-title">📌 지표명</p>', unsafe_allow_html=True)
    지표명 = st.text_input("kpi_name_input", value="지표명 입력")
    st.markdown('<p class="sb-title">🎯 지표 성격</p>', unsafe_allow_html=True)
    지표방향 = st.radio("direction_radio", ["상향", "하향"], horizontal=True)
    st.markdown('<p class="sb-title">⚖️ 가중치</p>', unsafe_allow_html=True)
    가중치_값 = st.number_input("weight_input", value=5.000, step=0.001, format="%.3f")
    st.markdown("---")
    display_name = 지표명 if 지표명 and 지표명 != "지표명 입력" else "미설정 지표"
    st.info(f"분석 대상: **{display_name}**")

st.title("⚖️ 중장기 성과지표 목표설정 및 한계점 분석기")

# --- 1. 실적 데이터 및 전망 ---
st.subheader("1. 실적 데이터 및 중장기 전망 입력")
실적_리스트 = []
m_cols = st.columns([5, 1, 3])

with m_cols[0]:
    st.markdown('<div class="main-header bg-past">과거 5개년 실적 (2021~2025)</div>', unsafe_allow_html=True)
    p_cols = st.columns(5)
    for i, year in enumerate(range(2021, 2026)):
        with p_cols[i]:
            st.markdown(f'<div class="sub-header">{year}</div>', unsafe_allow_html=True)
            val = st.number_input(f"p_{year}", value=round(100.0 + (i*5), 3), step=0.001, format="%.3f", key=f"v_{year}")
            실적_리스트.append(val)

with m_cols[1]:
    st.markdown('<div class="main-header bg-current">2026년 (예상)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">실적 입력</div>', unsafe_allow_html=True)
    예상_2026 = st.number_input("curr_2026", value=round(실적_리스트[-1] * 1.05, 3), step=0.001, format="%.3f", key="v_2026")

with m_cols[2]:
    st.markdown('<div class="main-header bg-future">중장기 실적 전망 (자동)</div>', unsafe_allow_html=True)
    f_cols = st.columns(3)
    X, Y = np.arange(6), np.array(실적_리스트 + [예상_2026])
    slope, intercept = np.polyfit(X, Y, 1)
    미래_전망 = []
    for i, year in enumerate(range(2027, 2030)):
        with f_cols[i]:
            st.markdown(f'<div class="sub-header">{year}</div>', unsafe_allow_html=True)
            f_val = round(slope * (6 + i) + intercept, 3)
            미래_전망.append(f_val)
            st.markdown(f'<div class="auto-res">{f_val:.3f}</div>', unsafe_allow_html=True)

avg3, std3 = round(np.mean(실적_리스트[-3:]), 3), round(np.std(실적_리스트[-3:]), 3)
avg5, std5 = round(np.mean(실적_리스트), 3), round(np.std(실적_리스트), 3)

st.markdown(f"""
<div class="guide-box">
    <span class="guide-title">📑 기초 통계 분석 데이터 (공부용)</span>
    • <b>시계열 분석 기법:</b> 입력하신 데이터는 <b>'선형 회귀 분석(Linear Regression)'</b>을 통해 중장기 추세선을 도출했습니다.<br>
    • <b>변동성 분석:</b> 과거 3개년 표준편차는 {std3:.3f}입니다. 이 값은 목표 설정 시 '도전성'의 척도가 됩니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if st.button("🚀 중장기 성과 및 한계점 분석 실행"):
    # 계산 로직
    기준치 = round(float(max(avg3, 실적_리스트[-1]) if 지표방향=="상향" else min(avg3, 실적_리스트[-1])), 3)
    방법별_설정 = [
        ("목표부여(2편차)", round(기준치 + 2*std3 if 지표방향=="상향" else 기준치 - 2*std3, 3)),
        ("목표부여(1편차)", round(기준치 + std3 if 지표방향=="상향" else 기준치 - std3, 3)),
        ("목표부여(120%)", round(기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8, 3)),
        ("목표부여(110%)", round(기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9, 3))
    ]

    결과_데이터 = []
    오차 = max(np.std(Y), 기준치 * 0.1)
    for 명칭, 최고 in 방법별_설정:
        최저 = round(기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2, 3)
        평점 = round(max(20.0, min(100.0, 20 + 80 * ((예상_2026 - 최저) / (최고 - 최저)))), 3)
        zp = (최고 - 예상_2026) / 오차 if 지표방향=="상향" else (예상_2026 - 최고) / 오차
        도전성_지수 = round((zp / 2.0) * 100, 3)
        단계 = "🏆 한계 혁신" if 도전성_지수 >= 150 else "🔥 적극 상향" if 도전성_지수 >= 80 else "📈 소극 개선" if 도전성_지수 >= 40 else "⚖️ 현상 유지"
        판정 = "⚠️ 한계" if (abs(최고 - 기준치) > (3 * std3) or abs(최고/기준치 - 1) > 0.3) else "✅ 유지"
        결과_데이터.append({
            "평가방법": 명칭, "지표성격": 지표방향, "기준치": 기준치, "최저목표": 최저, "최고목표": 최고,
            "예상실적": 예상_2026, "예상평점": 평점, "가중치": 가중치_값, "예상득점": round(평점 * (가중치_값 / 100.0), 3), 
            "도전성 단계": 단계, "추세치 분석결과": 판정, "raw_도전성": 도전성_지수
        })

    # --- 2. 분석 결과 테이블 ---
    st.subheader(f"2. {display_name} - 시나리오별 비교 분석 및 임계점 진단")
    df_res = pd.DataFrame(결과_데이터)
    st.table(df_res.drop(columns=['raw_도전성']).style.format({col: "{:.3f}" for col in ["기준치", "최저목표", "최고목표", "예상실적", "예상평점", "가중치", "예상득점"]}))

    # --- 💡 가이드 (표 바로 아래) ---
    st.markdown("""
    <div class="guide-box">
        <span class="guide-title">💡 분석 지표 가이드 (평가위원 대응용 지식)</span>
        <b>1. 도전성 단계 분석</b>: 목표치가 과거 표준편차의 몇 배(Sigma) 수준인지 분석합니다. 3배 이상은 통계적 임계점입니다.<br>
        <b>2. 추세치 분석결과</b>: 목표가 조직의 기초 체력을 벗어난 '한계치'에 도달했는지 판정하여 리스크를 관리합니다.
    </div>
    """, unsafe_allow_html=True)

    # --- 3. 그래프 ---
    st.subheader("3. 2029년 중장기 전망 및 목표 수준 시뮬레이션")
    fig, ax = plt.subplots(figsize=(11, 4))
    연도_축 = [f"'{y-2000}" for y in range(2021, 2030)]
    ax.plot(연도_축, slope * np.arange(9) + intercept, color='#CBD5E0', linestyle='--', label='중장기 추세선')
    ax.plot(연도_축[:5], Y[:5], marker='o', color='#2D6A4F', linewidth=2.5, label='과거 실적')
    ax.scatter(연도_축[5], 예상_2026, color='#D69E2E', s=200, marker='D', zorder=10, label='2026 예상')
    for i, row in df_res.iterrows():
        ax.scatter(연도_축[5], row['최고목표'], s=120, edgecolors='black', label=f"{row['평가방법']}")
    ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1.0, 1.0))
    st.pyplot(fig)

    # --- 4. 시나리오 작성 가이드 (최종 완성판) ---
    st.subheader("4. 도전적 목표 설정 시나리오 작성 가이드")
    
    유지가능 = [d for d in 결과_데이터 if d['추세치 분석결과'] == "✅ 유지"]
    
    if 유지가능:
        recom = max(유지가능, key=lambda x: x['raw_도전성'])
        conservative = min(결과_데이터, key=lambda x: x['raw_도전성'])
        
        # 중장기 전망과의 관계에 따른 자동 문구 생성
        is_aggressive = (지표방향 == "상향" and recom['최고목표'] >= 미래_전망[-1]) or (지표방향 == "하향" and recom['최고목표'] <= 미래_전망[-1])
        trend_analysis = f"예측 모델의 기대치({미래_전망[-1]:.3f})를 상회하는 공격적 설정" if is_aggressive else f"미래 불확실성을 고려하여 전망치({미래_전망[-1]:.3f})에 근접하게 수렴시킨 합리적 설정"
        keyword = "Stretch Goal(도전적 목표)" if is_aggressive else "내실 경영형 목표"

        st.markdown(f"""
        <div class="recom-box">
            <span class="guide-title" style="color:#2B6CB0;">📘 시나리오 기법(Scenario Planning) 기반 보고 가이드</span>
            본 가이드는 평가위원이 강조한 <b>'시나리오 기법'</b>을 적용하여 3가지 시나리오(보수-중립-도전)를 검토한 결과입니다.
            
            <div class="logic-box">
                <b>1. 다중 시나리오 설계 (Multi-Scenario Analysis)</b><br>
                • <b>[시나리오 A] 보수적 안정안</b>: 과거 평균 수준 유지 ({conservative['최고목표']:.3f})<br>
                • <b>[시나리오 B] 적극적 상향안 (추천)</b>: 추세 범위 내 최상단 도전 ({recom['최고목표']:.3f})<br>
                • <b>[시나리오 C] 한계 돌파형</b>: 통계적 임계점 초과 구간 (리스크 검토 대상)
            </div>

            <div class="logic-box">
                <b>2. 보고서용 논리적 근거 (상황에 맞춰 인용)</b><br>
                ① <b>방법론 명시:</b> "과거 5개년 실적의 성향을 반영한 <b>선형 회귀 시계열 모델</b>과 시나리오 기법을 병행하여 목표를 산출함"<br>
                ② <b>타당성 강조:</b> "제안된 목표({recom['최고목표']:.3f})는 {trend_analysis}을 통해 설정의 객관성과 정당성을 확보함"<br>
                ③ <b>리스크 관리:</b> "통계적 임계점(3-Sigma) 분석을 통해 무리한 설정을 지양하고, <b>도전성과 실현 가능성의 균형점</b>을 도출함"<br>
                ④ <b>결론:</b> "단순 개선을 넘어선 <b>{keyword}</b> 설정을 통해 조직의 역량을 결집하고 미래 성장을 견인하고자 함"
            </div>
            
            <p style="font-size: 13px; color: #718096; margin-top: 10px;">
            ※ 담당자 메모: 위 문구 중 본인의 지표 성향(도전/안정)에 가장 잘 맞는 문장을 선택하여 보고서에 활용하십시오.</p>
        </div>
        """, unsafe_allow_html=True)
