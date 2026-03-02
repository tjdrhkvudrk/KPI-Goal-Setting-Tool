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

# 2. CSS 스타일 정의
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
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; border: 1px solid #E2E8F0; }
    td { text-align: center !important; vertical-align: middle !important; border: 1px solid #E2E8F0; padding: 8px; }
    .merged-cell { background-color: #EDF2F7; font-weight: bold; color: #2D3748; width: 120px; }
    .strong-label { font-size: 20px !important; font-weight: 900 !important; color: #1A365D !important; margin-bottom: 12px; display: block; }
    
    .step-card { border-radius: 10px; padding: 15px; border-left: 5px solid; margin-bottom: 10px; background-color: #FFFFFF; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .step-1 { border-left-color: #E53E3E; } .step-2 { border-left-color: #DD6B20; }
    .step-3 { border-left-color: #38A169; } .step-4 { border-left-color: #A0AEC0; }
    
    .formula-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; background-color: white; }
    .formula-table th { border: 1px solid #E2E8F0; padding: 8px; text-align: center !important; }
    .formula-table td { border: 1px solid #E2E8F0; padding: 8px; text-align: left !important; }
    .up-col { background-color: #EBF8FF !important; color: #2B6CB0 !important; }
    .down-col { background-color: #FFF5F5 !important; color: #C53030 !important; }
    
    /* 타당성 분석 카드 스타일 */
    .valid-card { background-color: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .status-badge { padding: 4px 12px; border-radius: 15px; font-weight: bold; font-size: 14px; margin-bottom: 10px; display: inline-block; }
    .status-ok { background-color: #C6F6D5; color: #22543D; }
    .status-warn { background-color: #FED7D7; color: #822727; }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바 제어
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

# 4. 실적 데이터 처리
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
    <span style="font-weight:bold; color:#2D3748;">📑 실적 분석 참고내용</span><br>
    • <b>과거 3개년 실적 분석결과:</b> 평균 {avg3:.3f}, 표준편차 {std3:.3f}<br>
    • <b>과거 5개년 실적 분석결과:</b> 평균 {avg5:.3f}, 표준편차 {std5:.3f}<br>
    • <b>중장기 전망 분석결과:</b> 연평균 증가율 {cagr_f:.3f}%
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 5. 도전성 비교 테이블
기준치 = round(float(max(avg3, 실적_리스트[-1]) if 지표방향=="상향" else min(avg3, 실적_리스트[-1])), 3)
방법별 = [
    ("목표부여", "목표부여(2편차)", round(기준치 + 2*std3 if 지표방향=="상향" else 기준치 - 2*std3, 3)),
    ("목표부여", "목표부여(1편차)", round(기준치 + std3 if 지표방향=="상향" else 기준치 - std3, 3)),
    ("목표부여", "목표부여(120%)", round(기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8, 3)),
    ("목표부여", "목표부여(110%)", round(기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9, 3)),
    ("시나리오 분석", "낙관적 시나리오", round(slope_f * 6 + intercept_f + (std5 * 1.5) if 지표방향=="상향" else slope_f * 6 + intercept_f - (std5 * 1.5), 3)),
    ("시나리오 분석", "기본 시나리오", round(slope_f * 6 + intercept_f, 3)),
    ("시나리오 분석", "보수적 시나리오", round(slope_f * 6 + intercept_f - (std5 * 1.0) if 지표방향=="상향" else slope_f * 6 + intercept_f + (std5 * 1.0), 3))
]

결과_데이터 = []
오차 = max(np.std(Y_full), 기준치 * 0.1)
for 분류, 명칭, 최고 in 방법별:
    최저 = round(기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2, 3)
    denom = (최고 - 최저) if (최고 - 최저) != 0 else 1
    평점 = round(max(20.0, min(100.0, 20 + 80 * ((예상_2026 - 최저) / denom))), 3)
    도전성_지수 = round((((최고 - 예상_2026) / 오차 if 지표방향=="상향" else (예상_2026 - 최고) / 오차) / 2.0) * 100, 3)
    단계 = "🏆 한계 혁신" if 도전성_지수 >= 150 else "🔥 적극 상향" if 도전성_지수 >= 80 else "📈 소극 개선" if 도전성_지수 >= 40 else "⚖️ 현상 유지"
    
    # 판정 로직 복구
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

# 통합 산식 가이드 표
st.markdown(f"""
<div class="guide-box" style="padding:15px; margin-top:10px;">
    <span style="font-weight:bold; color:#2D3748; font-size:15px;">📋 평가방법별 목표 산식 및 설명 (상향/하향 비교 가이드)</span>
    <table class="formula-table">
        <thead>
            <tr>
                <th rowspan="2" style="background-color:#F7FAFC; width:14%;">평가방법</th>
                <th colspan="2" class="up-col">📈 상향 지표</th><th colspan="2" class="down-col">📉 하향 지표</th>
            </tr>
            <tr>
                <th class="up-col" style="width:16%;">산식</th><th class="up-col">상세 설명</th>
                <th class="down-col" style="width:16%;">산식</th><th class="down-col">상세 설명</th>
            </tr>
        </thead>
        <tbody>
            <tr><td style="font-weight:bold; text-align:center !important;">목표부여<br>(2편차)</td>
                <td>기준치 <b>+</b> (2 × std)</td><td>실적 변동폭의 2배를 더한 공격적 목표</td>
                <td>기준치 <b>-</b> (2 × std)</td><td>실적 변동폭의 2배를 뺀 타이트한 목표</td></tr>
            <tr><td style="font-weight:bold; text-align:center !important;">낙관적<br>시나리오</td>
                <td>추세선 <b>+</b> (1.5 × std)</td><td>미래 추세선에 혁신 가중치를 <b>더한</b> 지향점</td>
                <td>추세선 <b>-</b> (1.5 × std)</td><td>미래 추세선에서 혁신 가중치를 <b>뺀</b> 지향점</td></tr>
            <tr><td style="font-weight:bold; text-align:center !important;">기본<br>시나리오</td>
                <td colspan="2" style="text-align:center !important;">선형 추세값 (Linear Trend) 기반</td>
                <td colspan="2" style="text-align:center !important;">선형 추세값 (Linear Trend) 기반</td></tr>
            <tr><td style="font-weight:bold; text-align:center !important;">보수적<br>시나리오</td>
                <td>추세선 <b>-</b> (1.0 × std)</td><td>불확실성을 고려하여 낮게 잡은 하한선</td>
                <td>추세선 <b>+</b> (1.0 × std)</td><td>불확실성을 고려하여 높게 잡은 상한선</td></tr>
        </tbody>
    </table>
</div>
""", unsafe_allow_html=True)

# 6. 추세 그래프
st.markdown("---")
st.subheader("3. 중장기 추세 및 시나리오별 목표 궤적 분석")
years_all_label = [f"'{y-2000}" for y in range(2021, 2030)]
idx_future = np.arange(6, 10)
base_trend = slope_f * idx_future + intercept_f
line_optimistic = [예상_2026] + list(base_trend[1:] + (std5 * 1.5 if 지표방향=="상향" else -std5 * 1.5))
line_base = [예상_2026] + list(base_trend[1:])
line_conservative = [예상_2026] + list(base_trend[1:] - (std5 * 1.0 if 지표방향=="상향" else -std5 * 1.0))

fig, ax = plt.subplots(figsize=(13, 6.5))
ax.plot(years_all_label[:6], Y_full, marker='o', color='#2D3748', linewidth=3.5, label="과거 실적", zorder=20)
ax.scatter(years_all_label[5], 예상_2026, color='#F6E05E', s=250, marker='D', edgecolor='#2D3748', linewidth=2, label='2026 예상', zorder=25)
ax.plot(years_all_label[5:], line_optimistic, color='#3182CE', linestyle='--', linewidth=2, label='낙관적 시나리오')
ax.plot(years_all_label[5:], line_base, color='#718096', linestyle='--', linewidth=2, label='기본 시나리오')
ax.plot(years_all_label[5:], line_conservative, color='#D69E2E', linestyle='--', linewidth=2, label='보수적 시나리오')

colors = ['#E53E3E', '#DD6B20', '#38A169', '#805AD5']
for i, row in enumerate(결과_데이터[:4]):
    ax.scatter(years_all_label[5], row['최고목표'], s=150, color=colors[i], label=row['평가방법'], zorder=30, edgecolors='white')

ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1, 1), frameon=True, shadow=True)
ax.grid(axis='y', linestyle='-', alpha=0.1)
st.pyplot(fig)

# 목표 도전성 상세 판정 기준 카드
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<span style="font-weight: bold; font-size: 18px; color: #1A365D;">💡 목표 도전성 상세 판정 기준</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown("""<div class="step-card step-1"><span style="color:#E53E3E; font-weight:bold; font-size:16px;">🏆 1단계: 한계 혁신</span><br><span style="font-size:14px; color:#4A5568;">최상위 도전 수준 (추세선 대비 1.5σ 초과)</span></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="step-card step-2"><span style="color:#DD6B20; font-weight:bold; font-size:16px;">🔥 2단계: 적극 상향</span><br><span style="font-size:14px; color:#4A5568;">업무 개선 필요 수준 (추세선 대비 1.0~1.5σ)</span></div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="step-card step-3"><span style="color:#38A169; font-weight:bold; font-size:16px;">📈 3단계: 소극 개선</span><br><span style="font-size:14px; color:#4A5568;">완만한 추세 반영 (통계적 변동성 범위 내)</span></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="step-card step-4"><span style="color:#A0AEC0; font-weight:bold; font-size:16px;">⚖️ 4단계: 현상 유지</span><br><span style="font-size:14px; color:#4A5568;">최근 실적 유지 또는 보수적 목표</span></div>""", unsafe_allow_html=True)

# 7. 담당자 제언 및 타당성 분석 결과 복구
st.markdown("---")
st.subheader("🎯 4. 도전적 목표 설정 가이드 (담당자 제언)")

if 'f_idx' not in st.session_state: st.session_state.f_idx = 4
names = [r['평가방법'] for r in 결과_데이터]
compare_names = ["기준치"] + names

col_a, col_b = st.columns(2)
with col_a:
    st.markdown('<span class="strong-label">🎯 담당자 최종 선택</span>', unsafe_allow_html=True)
    선택방법 = st.selectbox("final_select", names, index=st.session_state.f_idx, key="box_f", label_visibility="collapsed")
    st.session_state.f_idx = names.index(선택방법)
with col_b:
    st.markdown('<span class="strong-label">⚖️ 비교 대상 (대조군)</span>', unsafe_allow_html=True)
    비교방법 = st.selectbox("compare_select", compare_names, index=0, key="box_c", label_visibility="collapsed")

sel = next(item for item in 결과_데이터 if item["평가방법"] == 선택방법)
sigma_lv = round(abs(sel['최고목표'] - 예상_2026) / std5, 2) if std5 != 0 else 0

# [복구된 부분] 목표 설정 타당성 검토 결과 카드
st.markdown('<span style="font-weight: bold; font-size: 18px; color: #1A365D;">🔍 목표 설정 타당성 검토 결과</span>', unsafe_allow_html=True)
status_class = "status-ok" if sel['분석결과'] == "✅ 유지" else "status-warn"
st.markdown(f"""
<div class="valid-card">
    <div class="status-badge {status_class}">{sel['분석결과']}</div>
    <div style="font-size: 14.5px; color: #2D3748;">
        • <b>판정 근거:</b> 선택하신 목표치(<b>{sel['최고목표']:.3f}</b>)는 통계적 신뢰 구간 및 과거 성장 추세를 반영할 때 
        {"<b>안정적인 달성 범위</b> 내에 있음" if sel['분석결과']=="✅ 유지" else "<b>통계적 임계치</b>를 초과하여 추가적인 자원 투입이나 혁신적 전략이 동반되어야 함"}을 확인했습니다.
    </div>
</div>
""", unsafe_allow_html=True)

if 비교방법 == "기준치":
    gap_val = round(abs(sel['최고목표'] - 기준치), 3)
    rate = round((gap_val / 기준치) * 100, 2) if 기준치 != 0 else 0
    logic_text = f"기준치(<b>{기준치:.3f}</b>) 대비 <b>{gap_val}</b>({rate}%)을 상향하여 <b>{sel['도전성 단계']}</b> 수준의 목표를 수립하였습니다."
else:
    comp = next(item for item in 결과_데이터 if item["평가방법"] == 비교방법)
    gap_val = round(abs(sel['최고목표'] - comp['최고목표']), 3)
    logic_text = f"대안 모델인 '{비교방법}(<b>{comp['최고목표']:.3f}</b>)' 대비 <b>{gap_val}</b>의 추가 상향을 통해 도전성을 확보하였습니다."

st.markdown(f"""
<div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <span style="background-color: #ebf8ff; color: #2b6cb0; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 14px;">AI 논리 분석 결과: {sel['도전성 단계']}</span>
        <span style="color: #718096; font-size: 13px;">작성일: {pd.Timestamp.now().strftime('%Y. %m. %d.')}</span>
    </div>
    <div style="line-height: 1.8; color: #4a5568;">
        <p><b>[보고서용 목표 설정 근거 초안]</b></p>
        1. 본 지표의 최종 목표치(<b>{sel['최고목표']:.3f}</b>)는 <b>{sel['평가방법']}</b>에 의거하여 산출되었습니다.<br>
        2. {logic_text}<br>
        3. 통계적 변동성 분석 결과, 본 목표는 과거 추세 대비 <b>{sigma_lv}σ</b> 수준의 수치로 평가되어 도전성이 충분한 것으로 판단됩니다.
    </div>
</div>
""", unsafe_allow_html=True)
