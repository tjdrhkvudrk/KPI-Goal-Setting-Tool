import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 및 설정
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

# 2. CSS 디자인 (원본 스타일 복구)
st.set_page_config(page_title="계량 성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; font-family: 'NanumGothic', sans-serif; }
    .sidebar-label { font-size: 16px; font-weight: 800; color: #1A202C; margin-top: 15px; margin-bottom: 8px; display: block; }
    .sidebar-white-box { background-color: white; border-radius: 8px; padding: 12px; border: 1px solid #E2E8F0; margin-bottom: 5px; }
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label, div[data-testid="stRadio"] > label { display: none !important; }
    .main-header { padding: 10px; color: white; text-align: center; font-weight: bold; margin-bottom: 5px; border-radius: 5px 5px 0 0; }
    .bg-past { background-color: #2D6A4F; }
    .bg-current { background-color: #D69E2E; }
    .bg-future { background-color: #4A5568; }
    .sub-header { background-color: #f1f3f5; padding: 5px; text-align: center; font-size: 13px; font-weight: bold; border: 1px solid #dee2e6; border-top: none; }
    .auto-res { background-color: #F8FAFC; border: 1px solid #dee2e6; height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .guide-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; line-height: 1.8; }
    .guide-title { font-weight: bold; color: #2D3748; font-size: 16px; margin-bottom: 10px; display: block; }
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; vertical-align: middle !important; border: 1px solid #E2E8F0; }
    .merged-cell { background-color: #EDF2F7; font-weight: bold; color: #2D3748; width: 120px; }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바 (단위 표기 삭제)
with st.sidebar:
    st.markdown('<span class="sidebar-label">📌 지표명</span>', unsafe_allow_html=True)
    지표명 = st.text_input("kpi_name", value="전략 KPI")
    st.markdown('<span class="sidebar-label">🎯 지표 성격</span>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-white-box">', unsafe_allow_html=True)
    지표방향 = st.radio("direction", ["상향", "하향"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-label">⚖️ 가중치</span>', unsafe_allow_html=True)
    가중치_값 = st.number_input("weight", value=5.000, step=0.001, format="%.3f")

st.title("📊 계량 성과지표 목표 설정 및 중장기 전망 시뮬레이터")

# ----------------------------------------------------------------
# 1~3번 섹션 (완벽 복구된 로직 유지)
# ----------------------------------------------------------------
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
    st.markdown('<div class="main-header bg-current">2026년 (예상)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">추세 기반 자동입력</div>', unsafe_allow_html=True)
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

avg3, std3 = round(np.mean(실적_리스트[-3:]), 3), round(np.std(실적_리스트[-3:]), 3)
avg5, std5 = round(np.mean(실적_리스트), 3), round(np.std(실적_리스트), 3)
cagr_f = round(((미래_전망[-1]/예상_2026)**(1/3)-1)*100, 3) if 예상_2026!=0 else 0

st.markdown(f"""
<div class="guide-box">
    <span class="guide-title">📑 실적 분석 참고내용</span>
    • <b>과거 3개년 실적 분석결과:</b> 평균 {avg3:.3f}, 표준편차 {std3:.3f}<br>
    • <b>과거 5개년 실적 분석결과:</b> 평균 {avg5:.3f}, 표준편차 {std5:.3f}<br>
    • <b>중장기 전망 분석결과:</b> 연평균 증가율 {cagr_f:.3f}%
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 2. 결과 테이블
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
    도전성_지수 = round((((최고 - 예상_2026) / 오차 if 지표방향=="상향" else (예상_2026 - 최고) / 오차) / 2.0) * 100, 3)
    단계 = "🏆 한계 혁신" if 도전성_지수 >= 150 else "🔥 적극 상향" if 도전성_지수 >= 80 else "📈 소극 개선" if 도전성_지수 >= 40 else "⚖️ 현상 유지"
    판정 = "✅ 유지" if (abs(최고 - 기준치) <= (3 * std3) and abs(최고/기준치 - 1) <= 0.3) else "⚠️ 한계"
    결과_데이터.append({"구분": 분류, "평가방법": 명칭, "기준치": 기준치, "최고목표": 최고, "예상평점": 평점, "예상득점": round(평점 * (가중치_값 / 100.0), 3), "도전성 단계": 단계, "분석결과": 판정})

st.subheader("2. 평가방법별 목표 도전성 비교")
html_table = f"""
<table style="width:100%; border-collapse: collapse; text-align: center;">
    <thead><tr style="background-color: #4A5568; color: white;"><th>구분</th><th>평가방법</th><th>기준치</th><th>최고목표</th><th>예상평점</th><th>예상득점</th><th>도전성 단계</th><th>분석결과</th></tr></thead>
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

# 3. 그래프 (목표부여 포인트 복구 확인)
st.subheader("3. 중장기 추세 및 시나리오별 목표 궤적 분석")
years_all_label = [f"'{y-2000}" for y in range(2021, 2030)]
idx_future = np.arange(6, 10)
base_trend = slope_f * idx_future + intercept_f
line_challenge = [예상_2026] + list(base_trend[1:] + (std5 * 1.5 if 지표방향=="상향" else -std5 * 1.5))
line_maintain = [예상_2026] + list(base_trend[1:])
line_conservative = [예상_2026] + list(base_trend[1:] - (std5 * 1.0 if 지표방향=="상향" else -std5 * 1.0))

fig, ax = plt.subplots(figsize=(13, 6.5))
ax.plot(years_all_label[:6], Y_full, marker='o', color='#2D3748', linewidth=3.5, label="과거 5개년 실적", zorder=20)
ax.scatter(years_all_label[5], 예상_2026, color='#F6E05E', s=250, marker='D', edgecolor='#2D3748', linewidth=2, label='2026 예상(기준점)', zorder=25)
ax.plot(years_all_label[5:], line_challenge, color='#3182CE', linestyle='--', linewidth=2, label='도전 시나리오')
ax.plot(years_all_label[5:], line_maintain, color='#718096', linestyle='--', linewidth=2, label='유지 시나리오')
ax.plot(years_all_label[5:], line_conservative, color='#D69E2E', linestyle='--', linewidth=2, label='보수 시나리오')

colors = ['#E53E3E', '#DD6B20', '#38A169', '#805AD5']
for i, row in enumerate(결과_데이터):
    if row['구분'] == "목표부여":
        ax.scatter(years_all_label[5], row['최고목표'], s=150, color=colors[i % 4], label=row['평가방법'], zorder=30, edgecolors='white')

ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1, 1), frameon=True, shadow=True)
ax.grid(axis='y', linestyle='-', alpha=0.1)
st.pyplot(fig)

# ----------------------------------------------------------------
# 4. 담당자 제언 (SyntaxError 해결 완료)
# ----------------------------------------------------------------
st.markdown("---")
st.subheader("🎯 4. 도전적 목표 설정 가이드 (담당자 제언)")

if 'f_idx' not in st.session_state: st.session_state.f_idx = 4
if 'c_idx' not in st.session_state: st.session_state.c_idx = 5

names = [r['평가방법'] for r in 결과_데이터]

c1, c2 = st.columns(2)
with c1:
    선택방법 = st.selectbox("🎯 담당자 최종 선택", names, index=st.session_state.f_idx, key="box_f")
    st.session_state.f_idx = names.index(선택방법)
with c2:
    비교방법 = st.selectbox("⚖️ 비교 대상 (대조군)", names, index=st.session_state.c_idx, key="box_c")
    st.session_state.c_idx = names.index(비교방법)

sel = next(item for item in 결과_데이터 if item["평가방법"] == 선택방법)
comp = next(item for item in 결과_데이터 if item["평가방법"] == 비교방법)
gap = round(abs(sel['최고목표'] - comp['최고목표']), 3)
sigma_lv = round(abs(sel['최고목표'] - 예상_2026) / std5, 2) if std5 != 0 else 0
imp_rate = round((abs(sel['최고목표'] - 예상_2026) / 예상_2026) * 100, 2) if 예상_2026 != 0 else 0

# HTML 카드 디자인 (st.markdown을 한 번에 깔끔하게 닫았습니다)
st.markdown(f"""
<div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <span style="background-color: #ebf8ff; color: #2b6cb0; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 14px;">
            AI 논리 분석 결과: {sel['도전성 단계']}
        </span>
        <span style="color: #718096; font-size: 13px;">분석 기준일: 2026. 02. 28.</span>
    </div>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px;">
        <div style="text-align: center; padding: 15px; background-color: #f7fafc; border-radius: 10px;">
            <div style="font-size: 12px; color: #a0aec0; margin-bottom: 5px;">목표 상향액(Gap)</div>
            <div style="font-size: 18px; font-weight: 800; color: #2d3748;">{gap}</div>
        </div>
        <div style="text-align: center; padding: 15px; background-color: #f7fafc; border-radius: 10px;">
            <div style="font-size: 12px; color: #a0aec0; margin-bottom: 5px;">변동성 대비(Sigma)</div>
            <div style="font-size: 18px; font-weight: 800; color: #2d3748;">{sigma_lv}σ</div>
        </div>
        <div style="text-align: center; padding: 15px; background-color: #f7fafc; border-radius: 10px;">
            <div style="font-size: 12px; color: #a0aec0; margin-bottom: 5px;">예상 대비 증감</div>
            <div style="font-size: 18px; font-weight: 800; color: #e53e3e;">{imp_rate}%</div>
        </div>
    </div>
    <div style="line-height: 1.8; color: #4a5568; border-top: 1px solid #edf2f7; padding-top: 20px;">
        <p><b>[보고서용 목표 설정 근거 초안]</b></p>
        1. 본 지표의 목표치(<b>{sel['최고목표']:.3f}</b>)는 예상 실적 대비 과거 5개년 변동폭의 <b>{sigma_lv}배</b> 수준으로, 
        단순 추세 연장을 탈피한 <b>{sel['도전성 단계']}</b> 목표임을 확인하였습니다.<br>
        2. 대안 모델인 '{비교방법}({comp['최고목표']:.3f})' 대비 <b>{gap}</b>의 추가 상향을 통해 성과 창출 의지를 적극 반영하였습니다.
    </div>
</div>
""", unsafe_allow_html=True)
