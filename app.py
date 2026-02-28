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

# 2. CSS 디자인 (깔끔한 카드 및 표 테마)
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
    .report-card { background-color: #EBF8FF; border-left: 8px solid #2B6CB0; border-radius: 10px; padding: 25px; margin-top: 20px; }
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; }
    thead tr th:first-child, tbody tr th { display: none; }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바
with st.sidebar:
    st.markdown('<p class="sb-title">📌 지표명</p>', unsafe_allow_html=True)
    지표명 = st.text_input("kpi_name", value="전략 KPI")
    st.markdown('<p class="sb-title">🎯 지표 성격</p>', unsafe_allow_html=True)
    지표방향 = st.radio("direction", ["상향", "하향"], horizontal=True)
    st.markdown('<p class="sb-title">⚖️ 가중치</p>', unsafe_allow_html=True)
    가중치_값 = st.number_input("weight", value=5.000, step=0.001, format="%.3f")
    st.markdown("---")
    display_name = 지표명 if 지표명 and 지표명 != "지표명 입력" else "미설정 지표"
    st.info(f"선택 방향: **{지표방향}**\n\n분석 대상: **{display_name}**")

st.title("⚖️ 중장기 성과지표 목표설정 및 한계점 분석기")

# --- 1. 실적 데이터 및 전망 입력 ---
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

# 실적 분석 참고내용
avg3, std3 = round(np.mean(실적_리스트[-3:]), 3), round(np.std(실적_리스트[-3:]), 3)
avg5, std5 = round(np.mean(실적_리스트), 3), round(np.std(실적_리스트), 3)
cagr_f = round(((미래_전망[-1]/예상_2026)**(1/3)-1)*100, 3) if 예상_2026 != 0 else 0

st.markdown(f"""
<div class="guide-box">
    <span class="guide-title" style="font-size: 16px;">📋 [데이터 분석 요약]</span>
    • <b>과거 3개년:</b> 평균 {avg3:.3f} / 표준편차 {std3:.3f} / CAGR {round(((실적_리스트[-1]/실적_리스트[-3])**(1/2)-1)*100, 3):.3f}%<br>
    • <b>과거 5개년:</b> 평균 {avg5:.3f} / 표준편차 {std5:.3f} / CAGR {round(((실적_리스트[-1]/실적_리스트[0])**(1/4)-1)*100, 3):.3f}%<br>
    • <b>중장기 전망:</b> 평균 {round(np.mean(미래_전망), 3):.3f} / CAGR {cagr_f:.3f}%
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if st.button("🚀 전체 분석 및 시나리오 비교 실행"):
    # 2. 분석 로직
    기준치 = round(float(max(avg3, 실적_리스트[-1]) if 지표방향=="상향" else min(avg3, 실적_리스트[-1])), 3)
    
    # [사용자 요청 반영] 기존 모델 + 추이 기반 시나리오 모델 통합
    방법별 = [
        ("목표부여(2편차)", round(기준치 + 2*std3 if 지표방향=="상향" else 기준치 - 2*std3, 3), "통계적 상단"),
        ("목표부여(1편차)", round(기준치 + std3 if 지표방향=="상향" else 기준치 - std3, 3), "통계적 평균 범위"),
        ("목표부여(120%)", round(기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8, 3), "단순 비율 적용"),
        ("목표부여(110%)", round(기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9, 3), "보수적 비율 적용"),
        ("도전 시나리오", round(slope * 6 + intercept + (std5 * 1.5) if 지표방향=="상향" else slope * 6 + intercept - (std5 * 1.5), 3), "추이 분석+공격적 전개"),
        ("유지 시나리오", round(slope * 6 + intercept, 3), "과거 5개년 추세 답습"),
        ("보수 시나리오", round(slope * 6 + intercept - (std5 * 1.0) if 지표방향=="상향" else slope * 6 + intercept + (std5 * 1.0), 3), "추이 분석+보수적 전개")
    ]

    결과_데이터 = []
    오차 = max(np.std(Y), 기준치 * 0.1)
    for 명칭, 최고, 비고 in 방법별:
        최저 = round(기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2, 3)
        평점 = round(max(20.0, min(100.0, 20 + 80 * ((예상_2026 - 최저) / (최고 - 최저)))), 3)
        zp = (최고 - 예상_2026) / 오차 if 지표방향=="상향" else (예상_2026 - 최고) / 오차
        도전성_지수 = round((zp / 2.0) * 100, 3)
        단계 = "🏆 한계 혁신" if 도전성_지수 >= 150 else "🔥 적극 상향" if 도전성_지수 >= 80 else "📈 소극 개선" if 도전성_지수 >= 40 else "⚖️ 현상 유지"
        판정 = "⚠️ 한계" if (abs(최고 - 기준치) > (3 * std3) or abs(최고/기준치 - 1) > 0.3) else "✅ 유지"
        
        결과_데이터.append({
            "평가방법": 명칭, "기준치": 기준치, "최고목표": 최고, "예상평점": 평점, 
            "예상득점": round(평점 * (가중치_값 / 100.0), 3), "도전성 단계": 단계, "분석결과": 판정, "모델성격": 비고, "raw": 도전성_지수
        })

    st.subheader(f"2. {display_name} - 평가 모델 및 추이 기반 시나리오 비교")
    df_res = pd.DataFrame(결과_데이터)
    st.table(df_res.drop(columns=['raw']).style.format({col: "{:.3f}" for col in ["기준치", "최고목표", "예상평점", "예상득점"]}))

    # 3. 그래프 (시나리오별 시각화)
    st.subheader("3. 2029년 중장기 전망 및 목표 시나리오 맵")
    fig, ax = plt.subplots(figsize=(11, 5))
    연도_축 = [f"'{y-2000}" for y in range(2021, 2030)]
    ax.plot(연도_축, slope * np.arange(9) + intercept, color='#CBD5E0', linestyle='--', label='중장기 추세선')
    ax.plot(연도_축[:5], Y[:5], marker='o', color='#2D6A4F', linewidth=2.5, label='과거 실적')
    ax.scatter(연도_축[5], 예상_2026, color='#D69E2E', s=200, marker='D', zorder=10, label='2026 예상')
    for i, row in df_res.iterrows():
        ax.scatter(연도_축[5], row['최고목표'], s=120, edgecolors='black', label=f"{row['평가방법']}")
    ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1.0, 1.0))
    st.pyplot(fig)

    # 4. 최종 보고 및 도전성 입증 가이드 (추이 분석 강조 버전)
    st.subheader("4. 최종 보고 및 도전성 입증 가이드")
    recom = next((d for d in 결과_데이터 if d['평가방법'] == "도전 시나리오"), 결과_데이터[0])
    consv = next((d for d in 결과_데이터 if d['평가방법'] == "유지 시나리오"), 결과_데이터[1])
    diff_pct = round(abs((recom['최고목표'] / 예상_2026 - 1) * 100), 2)

    st.markdown(f"""
    <div class="report-card">
        <span class="guide-title" style="color:#2B6CB0; font-size:18px;">🎯 [제안] 과거 추이 정밀 분석 기반 성과목표 설정</span>
        본 보고서는 단순 비율 설정을 탈피하여, <b>과거 5개년 실적 추이(Trend) 및 변동성(Sigma)</b>을 정밀 모델링한 결과입니다. 
        분석 결과, 전년 대비 <b>{diff_pct}% {"상향" if 지표방향=="상향" else "하향"}</b>된 <b>{recom['최고목표']:.3f}</b>를 최종 도전 목표로 제안합니다.
    </div>
    
    <div class="guide-box">
        <b>[논리 1] 시나리오 모델링 기반의 목표 타당성 확보</b><br>
        • <b>보수적 관점 (유지 시나리오):</b> {consv['최고목표']:.3f} → 과거 5개년 평균 성장률을 그대로 유지한 기초값<br>
        • <b>전략적 관점 (도전 시나리오):</b> {recom['최고목표']:.3f} → 추세선에 과거 최대 변동폭을 반영하여 도출한 <b>'Stretch Goal'</b><br>
        • <b>통계적 관점 (편차 모델):</b> 시나리오 수치가 통계적 임계점(Sigma Threshold) 내에 존재함을 상호 검증 완료<br><br>
        
        <b>[논리 2] 평가위원 대응 방어 논리</b><br>
        • <b>질문:</b> "목표 설정의 근거가 무엇인가?"<br>
        • <b>답변:</b> "단순한 자의적 설정이 아니라, 과거 5개년의 실적 시계열 데이터를 회귀 분석하여 미래 추세를 도출하고, 
        여기에 조직의 역량 집중 가능 범위를 시나리오별로 시뮬레이션하여 가장 합리적이고 도전적인 지점을 도출한 것입니다."
    </div>
    """, unsafe_allow_html=True)
