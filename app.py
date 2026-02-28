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

# 2. CSS 디자인 (사이드바 및 메인 레이아웃)
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; font-family: 'NanumGothic', sans-serif; }
    
    /* 사이드바 커스텀 */
    .sidebar-label { font-size: 16px; font-weight: 800; color: #1A202C; margin-top: 15px; margin-bottom: 8px; display: block; }
    .sidebar-white-box { background-color: white; border-radius: 8px; padding: 12px; border: 1px solid #E2E8F0; margin-bottom: 5px; }
    
    /* 기존 위젯 라벨 숨기기 */
    div[data-testid="stNumberInput"] label, 
    div[data-testid="stTextInput"] label, 
    div[data-testid="stRadio"] > label { display: none !important; }

    /* 메인 디자인 */
    .main-header { padding: 10px; color: white; text-align: center; font-weight: bold; margin-bottom: 5px; border-radius: 5px 5px 0 0; }
    .bg-past { background-color: #2D6A4F; }
    .bg-current { background-color: #D69E2E; }
    .bg-future { background-color: #4A5568; }
    .sub-header { background-color: #f1f3f5; padding: 5px; text-align: center; font-size: 13px; font-weight: bold; border: 1px solid #dee2e6; border-top: none; }
    .auto-res { background-color: #F8FAFC; border: 1px solid #dee2e6; height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .guide-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; line-height: 1.8; }
    .guide-title { font-weight: bold; color: #2D3748; font-size: 16px; margin-bottom: 10px; display: block; }
    .report-card { background-color: #EBF8FF; border-left: 8px solid #2B6CB0; border-radius: 10px; padding: 25px; margin-top: 20px; }
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; vertical-align: middle !important; border: 1px solid #E2E8F0; }
    .merged-cell { background-color: #EDF2F7; font-weight: bold; color: #2D3748; width: 120px; }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바 UI (이미지 요청사항 반영)
with st.sidebar:
    st.markdown('<span class="sidebar-label">📌 지표명</span>', unsafe_allow_html=True)
    지표명 = st.text_input("kpi_name", value="전략 KPI")
    
    st.markdown('<span class="sidebar-label">🎯 지표 성격</span>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-white-box">', unsafe_allow_html=True)
    지표방향 = st.radio("direction", ["상향", "하향"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<span class="sidebar-label">⚖️ 가중치</span>', unsafe_allow_html=True)
    가중치_값 = st.number_input("weight", value=5.000, step=0.001, format="%.3f")

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

X_past = np.arange(5)
Y_past = np.array(실적_리스트)
slope_p, intercept_p = np.polyfit(X_past, Y_past, 1)
suggested_2026 = round(slope_p * 5 + intercept_p, 3)

with m_cols[1]:
    st.markdown('<div class="main-header bg-current">2026년 (예측치)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">추세 기반 자동제안</div>', unsafe_allow_html=True)
    예상_2026 = st.number_input("curr_2026", value=suggested_2026, step=0.001, format="%.3f", key="v_2026")

with m_cols[2]:
    st.markdown('<div class="main-header bg-future">중장기 실적 전망 (자동)</div>', unsafe_allow_html=True)
    f_cols = st.columns(3)
    X_full, Y_full = np.arange(6), np.array(실적_리스트 + [예상_2026])
    slope_f, intercept_f = np.polyfit(X_full, Y_full, 1)
    미래_전망 = []
    for i, year in enumerate(range(2027, 2030)):
        with f_cols[i]:
            st.markdown(f'<div class="sub-header">{year}</div>', unsafe_allow_html=True)
            f_val = round(slope_f * (6 + i) + intercept_f, 3)
            미래_전망.append(f_val)
            st.markdown(f'<div class="auto-res">{f_val:.3f}</div>', unsafe_allow_html=True)

# [수정] 표준편차 포함 실적 분석 삼총사
avg3, std3 = round(np.mean(실적_리스트[-3:]), 3), round(np.std(실적_리스트[-3:]), 3)
avg5, std5 = round(np.mean(실적_리스트), 3), round(np.std(실적_리스트), 3)
avg_f, std_f = round(np.mean(미래_전망), 3), round(np.std(미래_전망), 3)

st.markdown(f"""
<div class="guide-box">
    <span class="guide-title">📑 실적 분석 참고내용</span>
    • <b>과거 3개년 실적 분석결과:</b> 평균 {avg3:.3f}, 표준편차 {std3:.3f}, 연평균 증가율 {round(((실적_리스트[-1]/실적_리스트[-3])**(1/2)-1)*100, 3) if 실적_리스트[-3]!=0 else 0:.3f}%<br>
    • <b>과거 5개년 실적 분석결과:</b> 평균 {avg5:.3f}, 표준편차 {std5:.3f}, 연평균 증가율 {round(((실적_리스트[-1]/실적_리스트[0])**(1/4)-1)*100, 3) if 실적_리스트[0]!=0 else 0:.3f}%<br>
    • <b>중장기 전망 분석결과:</b> 평균 {avg_f:.3f}, 표준편차 {std_f:.3f}, 연평균 증가율 {round(((미래_전망[-1]/예상_2026)**(1/3)-1)*100, 3) if 예상_2026!=0 else 0:.3f}%
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if st.button("🚀 전체 분석 및 시나리오 비교 실행"):
    기준치 = round(float(max(avg3, 실적_리스트[-1]) if 지표방향=="상향" else min(avg3, 실적_리스트[-1])), 3)
    
    방법별 = [
        ("목표부여", "목표부여(2편차)", round(기준치 + 2*std3 if 지표방향=="상향" else 기준치 - 2*std3, 3)),
        ("목표부여", "목표부여(1편차)", round(기준치 + std3 if 지표방향=="상향" else 기준치 - std3, 3)),
        ("목표부여", "목표부여(120%)", round(기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8, 3)),
        ("목표부여", "목표부여(110%)", round(기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9, 3)),
        ("시나리오 분석", "도전 시나리오", round(slope_f * 6 + intercept_f + (std5 * 1.5) if 지표방향=="상향" else slope_f * 6 + intercept_f - (std5 * 1.5), 3)),
        ("시나리오 분석", "유지 시나리오", round(slope_f * 6 + intercept_f, 3)),
        ("시나리오 분석", "보수 시나리오", round(slope_f * 6 + intercept_f - (std5 * 1.0) if 지표방향=="상향" else slope_f * 6 + intercept_f + (std5 * 1.0), 3))
    ]

    결과_데이터 = []
    오차 = max(np.std(Y_full), 기준치 * 0.1)
    for 분류, 명칭, 최고 in 방법별:
        최저 = round(기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2, 3)
        denom = (최고 - 최저) if (최고 - 최저) != 0 else 1
        평점 = round(max(20.0, min(100.0, 20 + 80 * ((예상_2026 - 최저) / denom))), 3)
        zp = (최고 - 예상_2026) / 오차 if 지표방향=="상향" else (예상_2026 - 최고) / 오차
        도전성_지수 = round((zp / 2.0) * 100, 3)
        단계 = "🏆 한계 혁신" if 도전성_지수 >= 150 else "🔥 적극 상향" if 도전성_지수 >= 80 else "📈 소극 개선" if 도전성_지수 >= 40 else "⚖️ 현상 유지"
        판정 = "⚠️ 한계" if (abs(최고 - 기준치) > (3 * std3) or abs(최고/기준치 - 1) > 0.3) else "✅ 유지"
        결과_데이터.append({"구분": 분류, "평가방법": 명칭, "기준치": 기준치, "최고목표": 최고, "예상평점": 평점, "예상득점": round(평점 * (가중치_값 / 100.0), 3), "도전성 단계": 단계, "분석결과": 판정})

    st.subheader("2. 평가방법별 목표 도전성 비교")
    # [수정 완료] NameError(결과_DATA -> 결과_데이터) 수정됨
    html_table = f"""
    <table style="width:100%; border-collapse: collapse; text-align: center;">
        <thead>
            <tr style="background-color: #4A5568; color: white;">
                <th>구분</th><th>평가방법</th><th>기준치</th><th>최고목표</th><th>예상평점</th><th>예상득점</th><th>도전성 단계</th><th>분석결과</th>
            </tr>
        </thead>
        <tbody>
            <tr><td rowspan="4" class="merged-cell">목표부여</td><td>{결과_데이터[0]['평가방법']}</td><td>{결과_데이터[0]['기준치']:.3f}</td><td>{결과_데이터[0]['최고목표']:.3f}</td><td>{결과_데이터[0]['예상평점']:.3f}</td><td>{결과_데이터[0]['예상득점']:.3f}</td><td>{결과_데이터[0]['도전성 단계']}</td><td>{결과_데이터[0]['분석결과']}</td></tr>
            <tr><td>{결과_데이터[1]['평가방법']}</td><td>{결과_데이터[1]['기준치']:.3f}</td><td>{결과_데이터[1]['최고목표']:.3f}</td><td>{결과_데이터[1]['예상평점']:.3f}</td><td>{결과_데이터[1]['예상득점']:.3f}</td><td>{결과_데이터[1]['도전성 단계']}</td><td>{결과_데이터[1]['분석결과']}</td></tr>
            <tr><td>{결과_데이터[2]['평가방법']}</td><td>{결과_데이터[2]['기준치']:.3f}</td><td>{결과_데이터[2]['최고목표']:.3f}</td><td>{결과_데이터[2]['예상평점']:.3f}</td><td>{결과_데이터[2]['예상득점']:.3f}</td><td>{결과_데이터[2]['도전성 단계']}</td><td>{결과_데이터[2]['분석결과']}</td></tr>
            <tr><td>{결과_데이터[3]['평가방법']}</td><td>{결과_데이터[3]['기준치']:.3f}</td><td>{결과_데이터[3]['최고목표']:.3f}</td><td>{결과_데이터[3]['예상평점']:.3f}</td><td>{결과_데이터[3]['예상득점']:.3f}</td><td>{결과_데이터[3]['도전성 단계']}</td><td>{결과_데이터[3]['분석결과']}</td></tr>
            <tr style="border-top: 2px solid #4A5568;"><td rowspan="3" class="merged-cell" style="background-color: #EBF8FF;">시나리오 분석</td><td>{결과_데이터[4]['평가방법']}</td><td>{결과_데이터[4]['기준치']:.3f}</td><td>{결과_데이터[4]['최고목표']:.3f}</td><td>{결과_데이터[4]['예상평점']:.3f}</td><td>{결과_데이터[4]['예상득점']:.3f}</td><td>{결과_데이터[4]['도전성 단계']}</td><td>{결과_데이터[4]['분석결과']}</td></tr>
            <tr><td>{결과_데이터[5]['평가방법']}</td><td>{결과_데이터[5]['기준치']:.3f}</td><td>{결과_데이터[5]['최고목표']:.3f}</td><td>{결과_데이터[5]['예상평점']:.3f}</td><td>{결과_데이터[5]['예상득점']:.3f}</td><td>{결과_데이터[5]['도전성 단계']}</td><td>{결과_데이터[5]['분석결과']}</td></tr>
            <tr><td>{결과_데이터[6]['평가방법']}</td><td>{결과_데이터[6]['기준치']:.3f}</td><td>{결과_데이터[6]['최고목표']:.3f}</td><td>{결과_데이터[6]['예상평점']:.3f}</td><td>{결과_데이터[6]['예상득점']:.3f}</td><td>{결과_데이터[6]['도전성 단계']}</td><td>{결과_데이터[6]['분석결과']}</td></tr>
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)

    # 가이드 및 그래프 섹션 (동일 유지)
    st.markdown(f"""
    <div class="guide-box">
        <span class="guide-title">💡 분석 지표 가이드</span>
        <b>1. 도전성 단계 분석 (과거 추세 대비 상향 정도)</b><br>
        • 🏆 <b>한계 혁신</b>: 목표치가 예상 실적보다 표준편차의 3배 이상 높은 경우로 파격적 목표 수준<br>
        • 🔥 <b>적극 상향</b>: 과거 변동폭의 1.6배~3배 수준으로 공격적 목표 수준<br>
        • 📈 <b>소극 개선</b>: 과거 변동 범위 내에 존재하며 완만한 우상향 추세를 따르는 수준<br>
        • ⚖️ <b>현상 유지</b>: 관리 중심 목표 수준<br><br>
        <b>2. 추세치 분석결과 (한계 판정 기준)</b><br>
        • ⚠️ <b>한계</b>: 과거 표준편차의 3배를 초과하거나 30% 이상 급변하여 역량상 임계점에 도달했음을 의미
    </div>
    """, unsafe_allow_html=True)

    st.subheader("3. 중장기 추세 및 시나리오별 목표 궤적 분석")
    years_all = [f"'{y-2000}" for y in range(2021, 2030)]
    years_past = years_all[:6]
    years_future = years_all[5:]
    idx_future = np.arange(6, 10)
    base_trend = slope_f * idx_future + intercept_f
    
    line_challenge = [예상_2026] + list(base_trend[1:] + (std5 * 1.5 if 지표방향=="상향" else -std5 * 1.5))
    line_maintain = [예상_2026] + list(base_trend[1:])
    line_conservative = [예상_2026] + list(base_trend[1:] - (std5 * 1.0 if 지표방향=="상향" else -std5 * 1.0))

    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(years_all, slope_f * np.arange(9) + intercept_f, color='#EDF2F7', linestyle=':', label='기초 추세선', zorder=1)
    ax.plot(years_future, line_challenge, color='#3182CE', linestyle='--', linewidth=2, label='도전 시나리오', zorder=2)
    ax.plot(years_future, line_maintain, color='#718096', linestyle='--', linewidth=2, label='유지 시나리오', zorder=2)
    ax.plot(years_future, line_conservative, color='#D69E2E', linestyle='--', linewidth=2, label='보수 시나리오', zorder=2)
    ax.fill_between(years_future, line_conservative, line_challenge, color='#EBF8FF', alpha=0.3)
    ax.plot(years_past, Y_full, marker='o', color='#2D3748', linewidth=3.5, label="과거 5개년 실적", zorder=3)

    ax.scatter(years_all[5], 예상_2026, color='#F6E05E', s=250, marker='D', edgecolor='#2D3748', linewidth=2, label='2026 예상(기준점)', zorder=10)

    for row in 결과_데이터:
        if row['구분'] == "목표부여":
            ax.scatter(years_all[5], row['최고목표'], s=120, zorder=5, edgecolors='white', linewidth=1, label=f"{row['평가방법']}")

    ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1, 1), frameon=True, shadow=True)
    ax.grid(axis='y', linestyle='-', alpha=0.1)
    st.pyplot(fig)
