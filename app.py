import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 설정 (고정)
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
    return font_name if os.path.exists(font_path) else None

font_name = load_korean_font()

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
    .recom-box { background-color: #FFF5F5; border: 1px solid #E53E3E; border-radius: 10px; padding: 20px; margin-top: 15px; border-left: 8px solid #E53E3E; }
    .logic-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-top: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .guide-title { font-weight: bold; color: #2D3748; font-size: 17px; margin-bottom: 10px; display: block; }
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
st.markdown(f"""<div class="guide-box"><span class="guide-title">📑 기초 통계 데이터 분석 결과</span>• 과거 3개년 평균: {avg3:.3f} / 표준편차(Sigma): {std3:.3f} (도전성 판정의 기준선)</div>""", unsafe_allow_html=True)

st.markdown("---")

if st.button("🚀 중장기 성과 및 한계점 분석 실행"):
    # 분석 로직
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
        결과_데이터.append({"평가방법": 명칭, "지표성격": 지표방향, "기준치": 기준치, "최저목표": 최저, "최고목표": 최고, "예상실적": 예상_2026, "예상평점": 평점, "가중치": 가중치_값, "예상득점": round(평점 * (가중치_값 / 100.0), 3), "도전성 단계": 단계, "추세치 분석결과": 판정, "raw_도전성": 도전성_지수})

    # 2. 결과 테이블 및 분석 가이드 (기존 완벽한 버전 복구)
    st.subheader(f"2. {display_name} - 평가방법별 비교 분석 결과 및 임계점 진단")
    df_res = pd.DataFrame(결과_데이터)
    st.table(df_res.drop(columns=['raw_도전성']).style.format({col: "{:.3f}" for col in ["기준치", "최저목표", "최고목표", "예상실적", "예상평점", "가중치", "예상득점"]}))

    st.markdown("""<div class="guide-box"><span class="guide-title">💡 분석 지표 상세 가이드 (도전성 판정 기준)</span><b>1. 도전성 단계 분석</b>: 🏆한계 혁신(압도적 도전), 🔥적극 상향(공격적 목표), 📈소극 개선(추세 유지), ⚖️현상 유지(관리 중심)<br><b>2. 추세치 분석결과</b>: ⚠️한계 판정은 과거 변동폭(3-Sigma)을 초과하여 실현 가능성이 매우 낮음을 의미합니다.</div>""", unsafe_allow_html=True)

    # 3. 그래프 (기존 완벽한 버전 유지)
    st.subheader("3. 2029년 중장기 전망 및 목표 수준 시뮬레이션")
    fig, ax = plt.subplots(figsize=(11, 4))
    연도_축 = [f"'{y-2000}" for y in range(2021, 2030)]
    ax.plot(연도_축, slope * np.arange(9) + intercept, color='#CBD5E0', linestyle='--', label='중장기 추세선')
    ax.plot(연도_축[:5], Y[:5], marker='o', color='#2D6A4F', linewidth=2.5, label='과거 실적')
    ax.scatter(연도_축[5], 예상_2026, color='#D69E2E', s=200, marker='D', zorder=10, label='2026 예상')
    for i, row in df_res.iterrows():
        ax.scatter(연도_축[5], row['최고목표'], s=120, edgecolors='black', label=f"{row['평가방법']}")
    ax.legend(prop={'family': font_name} if font_name else None, loc='upper left', bbox_to_anchor=(1.0, 1.0))
    st.pyplot(fig)

    # 4. 도전적 목표 설정 시나리오 작성 가이드 (자동 분석 기반 고도화)
    st.subheader("4. 도전적 목표 설정 시나리오 작성 가이드")
    
    유지가능 = [d for d in 결과_데이터 if d['추세치 분석결과'] == "✅ 유지"]
    
    if 유지가능:
        recom = max(유지가능, key=lambda x: x['raw_도전성'])
        consv = min(결과_데이터, key=lambda x: x['raw_도전성'])
        limit_val = next((d['최고목표'] for d in 결과_데이터 if d['추세치 분석결과'] == "⚠️ 한계"), "산출 범위 초과")
        
        diff_pct = abs(round((recom['최고목표'] / 예상_2026 - 1) * 100, 2))
        is_high = (지표방향 == "상향" and recom['최고목표'] >= 미래_전망[-1]) or (지표방향 == "하향" and recom['최고목표'] <= 미래_전망[-1])
        
        st.markdown(f"""
        <div class="recom-box">
            <span class="guide-title" style="color:#C53030;">📌 실시간 분석 기반 시나리오 추천 ([{recom['평가방법']}] 채택)</span>
            분석 결과, <b>{recom['도전성 단계']}</b> 수준의 목표가 가장 적합한 시나리오로 도출되었습니다.
            
            <div class="logic-card">
                <b>가이드 1. 시나리오 기법 기반 비교 분석 (Scenario Planning)</b><br>
                평가위원 권고에 따라 3대 시나리오를 시뮬레이션한 결과입니다.<br>
                • <b>[보수적 시나리오]</b> 실적 유지 중심의 안정적 목표 ({consv['최고목표']:.3f})<br>
                • <b>[도전적 시나리오]</b> 역량 집중을 통한 성과 상향 목표 ({recom['최고목표']:.3f}) <span class="point-txt">← 최종 채택안</span><br>
                • <b>[임계 시나리오]</b> 통계적 달성 불확실성 구간 ({limit_val})
            </div>

            <div class="logic-card">
                <b>가이드 2. 통계적 도전성 입증 근거 (Statistical Justification)</b><br>
                • <b>Sigma 분석</b>: 제안 목표는 과거 변동폭({std3:.3f})의 <b>{round(abs(recom['최고목표']-기준치)/std3, 2)}배</b> 수준으로, 통계적 유의미성 내에서 가장 공격적인 수치입니다.<br>
                • <b>정당성 확보</b>: 단순 상향이 아닌, 과거 5개년 실적의 표준편차를 기반으로 <b>'근거 있는 도전성'</b>을 확보하였습니다.
            </div>

            <div class="logic-card">
                <b>가이드 3. 미래 추세 대응 전략 (Trend-driven Logic)</b><br>
                • <b>예측 모델 연계</b>: 선형 회귀 분석 결과 도출된 중장기 전망치({미래_전망[-1]:.3f})를 고려할 때, 본 목표는 <b>{"성장을 가속화하는" if is_high else "내실을 다지며 성장을 견인하는"}</b> 전략적 포지션을 취하고 있습니다.
            </div>

            <div class="logic-card">
                <b>[보고서 인용 문구 초안]</b><br>
                "본 목표는 시나리오 기법을 적용하여 다각적 시뮬레이션을 거쳤으며, 과거 변동성(Standard Deviation) 대비 도전적인 수준인 <b>{recom['최고목표']:.3f}</b>(전년 실적 대비 {diff_pct}% 상향)를 최종안으로 도출함. 이는 통계적 임계점 이내의 최상단 목표로서 <b>도전성과 실현 가능성의 최적 균형</b>을 구현한 결과임."
            </div>
        </div>
        """, unsafe_allow_html=True)
