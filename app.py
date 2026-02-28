import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests
from io import BytesIO

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

# 2. CSS 디자인
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; font-family: 'NanumGothic', sans-serif; }
    .main-header { padding: 10px; color: white; text-align: center; font-weight: bold; margin-bottom: 5px; border-radius: 5px 5px 0 0; }
    .bg-past { background-color: #2D6A4F; }
    .bg-current { background-color: #D69E2E; }
    .bg-future { background-color: #4A5568; }
    .sub-header { background-color: #f1f3f5; padding: 5px; text-align: center; font-size: 13px; font-weight: bold; border: 1px solid #dee2e6; border-top: none; }
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label, div[data-testid="stRadio"] > label { display: none !important; }
    .auto-res { background-color: #F8FAFC; border: 1px solid #dee2e6; height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .guide-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; line-height: 1.8; }
    .guide-title { font-weight: bold; color: #2D3748; font-size: 16px; margin-bottom: 10px; display: block; }
    .report-card { background-color: #EBF8FF; border-left: 8px solid #2B6CB0; border-radius: 10px; padding: 25px; margin-top: 20px; }
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; vertical-align: middle !important; border: 1px solid #E2E8F0; }
    .merged-cell { background-color: #EDF2F7; font-weight: bold; color: #2D3748; width: 120px; }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바
with st.sidebar:
    st.markdown('<p style="font-size:16px; font-weight:800; color:#1A202C;">📌 지표명</p>', unsafe_allow_html=True)
    지표명 = st.text_input("kpi_name", value="전략 KPI")
    st.markdown('<p style="font-size:16px; font-weight:800; color:#1A202C;">🎯 지표 성격</p>', unsafe_allow_html=True)
    지표방향 = st.radio("direction", ["상향", "하향"], horizontal=True)
    st.markdown('<p style="font-size:16px; font-weight:800; color:#1A202C;">⚖️ 가중치</p>', unsafe_allow_html=True)
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

# [수정 불가 포인트] 2026년 예상치 자동 제안 (사용자 수정 가능)
X_past = np.arange(5)
Y_past = np.array(실적_리스트)
slope_p, intercept_p = np.polyfit(X_past, Y_past, 1)
suggested_2026 = round(slope_p * 5 + intercept_p, 3)

with m_cols[1]:
    st.markdown('<div class="main-header bg-current">2026년 (예상)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">추세 기반 수정 가능</div>', unsafe_allow_html=True)
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

# [원본 유지] 실적 분석 참고내용
avg3, std3 = round(np.mean(실적_리스트[-3:]), 3), round(np.std(실적_리스트[-3:]), 3)
avg5, std5 = round(np.mean(실적_리스트), 3), round(np.std(실적_리스트), 3)
avg_f = round(np.mean(미래_전망), 3)

st.markdown(f"""
<div class="guide-box">
    <span class="guide-title">📑 실적 분석 참고내용</span>
    • <b>과거 3개년 실적 분석결과:</b> 평균 {avg3:.3f}, 표준편차 {std3:.3f}, 연평균 증가율 {round(((실적_리스트[-1]/실적_리스트[-3])**(1/2)-1)*100, 3) if 실적_리스트[-3]!=0 else 0:.3f}%<br>
    • <b>과거 5개년 실적 분석결과:</b> 평균 {avg5:.3f}, 표준편차 {std5:.3f}, 연평균 증가율 {round(((실적_리스트[-1]/실적_리스트[0])**(1/4)-1)*100, 3) if 실적_리스트[0]!=0 else 0:.3f}%<br>
    • <b>중장기 전망 분석결과:</b> 평균 {avg_f:.3f}, 연평균 증가율 {round(((미래_전망[-1]/예상_2026)**(1/3)-1)*100, 3) if 예상_2026!=0 else 0:.3f}%
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

    # [수정 불가 포인트] 2번 제목 및 표 구성 유지
    st.subheader("2. 평가방법별 목표 도전성 비교")
    
    df_export = pd.DataFrame(결과_데이터)
    csv = df_export.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 분석 결과 Excel(CSV)로 저장", csv, f"{지표방향}_{지표명}_분석결과.csv", "text/csv")

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

    # [완벽 복구 가이드]
    st.markdown(f"""
    <div class="guide-box">
        <span class="guide-title">💡 분석 지표 가이드</span>
        <b>1. 도전성 단계 분석 (과거 추세 대비 상향 정도)</b><br>
        • 🏆 <b>한계 혁신</b>: 목표치가 예상 실적보다 표준편차의 3배 이상 높은 경우로, 과거의 흐름을 완전히 벗어난 파격적 목표 수준<br>
        • 🔥 <b>적극 상향</b>: 목표치가 과거 변동폭의 1.6배~3배 수준으로, 과거 성장세를 상회하는 공격적 목표 수준<br>
        • 📈 <b>소극 개선</b>: 목표치가 과거 변동 범위 내에 존재하며, 과거의 완만한 우상향 추세를 따르는 안정적 수준<br>
        • ⚖️ <b>현상 유지</b>: 목표치가 예상 실적과 유사하거나 과거 평균 수준에 머무르는 경우로, 관리 중심 목표 수준<br><br>
        <b>2. 추세치 분석결과 (한계 판정 기준)</b><br>
        • ⚠️ <b>한계</b>: 목표치가 과거 표준편차의 3배를 초과하거나 30% 이상 급변하여 역량상 임계점에 도달했음을 의미합니다.<br><br>
        <b>3. 시나리오 분석 산식 및 평가 기준 (추이 분석 기반)</b><br>
        • <b>도전 시나리오:</b> 과거 5개년 추세선 상의 2026년 기대값 {"+" if 지표방향=="상향" else "-"} (과거 5개년 표준편차 × 1.5). 과거 최대 변동폭 이상의 성과를 가정한 수준입니다.<br>
        • <b>유지 시나리오:</b> 회귀 분석 추세선에 따른 2026년 예측값 (y = 기울기 × 연도 + 절편). 과거의 성장 흐름이 그대로 지속될 때의 기대 수준입니다.<br>
        • <b>보수 시나리오:</b> 과거 5개년 추세선 상의 2026년 기대값 {"-" if 지표방향=="상향" else "+"} (과거 5개년 표준편차 × 1.0). 대내외 여건 악화로 성장이 정체될 경우를 가정한 수준입니다.
    </div>
    """, unsafe_allow_html=True)

    # --- [업데이트] 3. 그래프 (시나리오 궤적 통합 시각화) ---
    st.subheader("3. 중장기 추세 및 시나리오별 목표 궤적 분석")
    
    # 데이터 매핑
    years_all = [f"'{y-2000}" for y in range(2021, 2030)]
    years_past = years_all[:6]   # '21~'26
    years_future = years_all[5:]  # '26~'29
    
    # 시나리오 미래 궤적 계산 (2026~2029)
    idx_future = np.arange(6, 10)
    base_trend = slope_f * idx_future + intercept_f
    
    # 궤적별 리스트 생성 (2026 예상치에서 분기)
    line_challenge = [예상_2026] + list(base_trend[1:] + (std5 * 1.5 if 지표방향=="상향" else -std5 * 1.5))
    line_maintain = [예상_2026] + list(base_trend[1:])
    line_conservative = [예상_2026] + list(base_trend[1:] - (std5 * 1.0 if 지표방향=="상향" else -std5 * 1.0))

    fig, ax = plt.subplots(figsize=(13, 6.5))
    
    # 1. 배경 추세선 (전체 구간)
    ax.plot(years_all, slope_f * np.arange(9) + intercept_f, color='#EDF2F7', linestyle=':', label='기본 추세선(Base)', zorder=1)
    
    # 2. 과거 실적 및 예상 (굵은 실선)
    ax.plot(years_past, Y_full, marker='o', color='#2D3748', linewidth=3.5, label=f"과거 실적 및 '26 예상", zorder=5)

    # 3. 미래 시나리오 궤적 (점선 및 마커)
    ax.plot(years_future, line_challenge, color='#3182CE', linestyle='--', linewidth=2, marker='^', markersize=8, label='도전 시나리오')
    ax.plot(years_future, line_maintain, color='#718096', linestyle='--', linewidth=2, marker='s', markersize=7, label='유지 시나리오')
    ax.plot(years_future, line_conservative, color='#D69E2E', linestyle='--', linewidth=2, marker='v', markersize=8, label='보수 시나리오')
    
    # 미래 범위 강조 채우기
    ax.fill_between(years_future, line_conservative, line_challenge, color='#EBF8FF', alpha=0.3)

    # 4. 목표부여(통계모델) 2026년 포인트들 (비교용 이정표)
    for row in 결과_데이터:
        if row['구분'] == "목표부여":
            ax.scatter(years_all[5], row['최고목표'], s=150, zorder=10, 
                       edgecolors='white', linewidth=2, label=f"Ref: {row['평가방법']}")

    # 디자인 마무리
    ax.set_title(f"[{지표명}] 중장기 목표 시나리오 시뮬레이션", pad=20, fontproperties=font_prop, fontsize=16)
    ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1, 1), frameon=True, shadow=True)
    ax.grid(axis='y', linestyle='-', alpha=0.1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Y축 범위 최적화
    all_vals = list(Y_full) + line_challenge + line_conservative
    ax.set_ylim(min(all_vals)*0.9, max(all_vals)*1.1)

    st.pyplot(fig)

    # 4. 최종 보고 가이드
    st.markdown(f"""
    <div class="report-card">
        <span style="font-weight:bold; color:#2B6CB0; font-size:18px;">🎯 시나리오 분석 기반 성과목표 제안</span><br><br>
        본 보고서는 <b>과거 5개년 실적 추이 정밀 분석</b>을 기반으로 실적 변동성을 모델링하였습니다.<br>
        <b>지표 성격({지표방향})</b>을 고려하여, 추세 대비 도전성이 확보된 <b>[도전 시나리오]</b>를 최종 목표(<b>{결과_데이터[4]['최고목표']:.3f}</b>)로 제안합니다.
    </div>
    """, unsafe_allow_html=True)
