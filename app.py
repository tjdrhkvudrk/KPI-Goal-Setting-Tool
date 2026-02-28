import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 설정 (기존 완벽 기능 유지)
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

# 2. CSS 디자인 (가독성 및 신뢰감 있는 블루톤 테마)
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
    
    /* 가이드 박스 스타일 */
    .summary-box { background-color: #EBF8FF; border-left: 8px solid #2B6CB0; border-radius: 10px; padding: 25px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .detail-box { background-color: #F7FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 25px; margin-top: 20px; }
    .logic-card { background-color: white; border: 1px solid #CBD5E0; border-radius: 8px; padding: 18px; margin-top: 15px; }
    
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

# 기초 통계 데이터 분석 (복구)
avg3, std3 = round(np.mean(실적_리스트[-3:]), 3), round(np.std(실적_리스트[-3:]), 3)
avg5, std5 = round(np.mean(실적_리스트), 3), round(np.std(실적_리스트), 3)
avg_f = round(np.mean(미래_전망), 3)
cagr3 = round(((실적_리스트[-1]/실적_리스트[-3])**(1/2)-1)*100, 3) if 실적_리스트[-3] != 0 else 0
cagr_f = round(((미래_전망[-1]/예상_2026)**(1/3)-1)*100, 3) if 예상_2026 != 0 else 0

st.markdown(f"""
<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 15px; margin-top: 10px;">
    <b>📑 실적 통계 분석:</b> 과거 3개년 평균 {avg3:.3f} / 5개년 평균 {avg5:.3f} / 향후 3년 CAGR {cagr_f:.3f}% (변동성 Sigma: {std3:.3f})
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if st.button("🚀 중장기 성과 및 한계점 분석 실행"):
    # 2. 결과 분석 로직
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

    st.subheader(f"2. {display_name} - 시나리오별 비교 분석 결과")
    df_res = pd.DataFrame(결과_데이터)
    st.table(df_res.drop(columns=['raw_도전성']).style.format({col: "{:.3f}" for col in ["기준치", "최저목표", "최고목표", "예상실적", "예상평점", "가중치", "예상득점"]}))

    # 3. 그래프 (기존 완벽 기능 유지)
    st.subheader("3. 2029년 중장기 전망 시뮬레이션")
    fig, ax = plt.subplots(figsize=(11, 4))
    연도_축 = [f"'{y-2000}" for y in range(2021, 2030)]
    ax.plot(연도_축, slope * np.arange(9) + intercept, color='#CBD5E0', linestyle='--', label='중장기 추세선')
    ax.plot(연도_축[:5], Y[:5], marker='o', color='#2D6A4F', linewidth=2.5, label='과거 실적')
    ax.scatter(연도_축[5], 예상_2026, color='#D69E2E', s=200, marker='D', zorder=10, label='2026 예상')
    for i, row in df_res.iterrows():
        ax.scatter(연도_축[5], row['최고목표'], s=120, edgecolors='black', label=f"{row['평가방법']}")
    ax.legend(prop={'family': font_prop.get_name()} if font_prop else None, loc='upper left', bbox_to_anchor=(1.0, 1.0))
    st.pyplot(fig)

    # 4. 최종 성과목표 설정 제안 및 도전성 입증 가이드 (완전체)
    st.subheader("4. 최종 성과목표 설정 제안 및 도전성 입증 가이드")
    
    유지가능 = [d for d in 결과_데이터 if d['추세치 분석결과'] == "✅ 유지"]
    if 유지가능:
        recom = max(유지가능, key=lambda x: x['raw_도전성'])
        compare_target = min(유지가능, key=lambda x: x['raw_도전성'])
        limit_val = next((d['최고목표'] for d in 결과_데이터 if d['추세치 분석결과'] == "⚠️ 한계"), "통계적 임계점 초과")
        
        diff_pct = round(abs((recom['최고목표'] / 예상_2026 - 1) * 100), 2)
        direction_txt = "상향" if 지표방향 == "상향" else "하향"

        # [Summary 박스]
        st.markdown(f"""
        <div class="summary-box">
            <h3 style="color: #2C5282; margin-top: 0;">🎯 [최종 제안] 성과목표 설정 시나리오 요약</h3>
            <p style="font-size: 16px; line-height: 1.7; color: #2D3748;">
                본 지표는 <b>[{recom['평가방법']}]</b> 시나리오를 최종 목표 설정 모델로 채택하였습니다. <br>
                보수적 설정 모델인 [{compare_target['평가방법']}] 대비 <b>도전성을 대폭 강화</b>하였으며, 
                2026년 예상 실적 대비 <b>{diff_pct}% {direction_txt}</b>된 <b>{recom['최고목표']:.3f}</b>를 최종 목표치로 제안합니다.
            </p>
            <div style="background-color: white; padding: 10px 15px; border-radius: 5px; border: 1px solid #BEE3F8; display: inline-block;">
                <span style="color: #2B6CB0; font-weight: bold;">핵심 전략:</span> {recom['도전성 단계']} 및 통계적 임계점(3-Sigma) 내 최상단 목표 지향
            </div>
        </div>
        """, unsafe_allow_html=True)

        # [상세 입증 내용 박스]
        st.markdown(f"""
        <div class="detail-box">
            <h4 style="color: #2D3748; border-bottom: 2px solid #CBD5E0; padding-bottom: 10px;">🔍 목표 설정의 과학적 근거 및 도전성 입증</h4>
            
            <div class="logic-card">
                <h5 style="color: #2B6CB0; margin-top:0;">1️⃣ 시나리오 기법 (Scenario Planning) 적용</h5>
                평가위원 권고 사항을 반영하여 미래 실적 시나리오를 3단계로 분석하였습니다.
                <ul>
                    <li><b>[보수 시나리오]</b> {compare_target['평가방법']} (목표: {compare_target['최고목표']:.3f}) → 과거 추세 답습형</li>
                    <li><b>[도전 시나리오]</b> {recom['평가방법']} (목표: {recom['최고목표']:.3f}) → <b>역량 집중 및 성과 견인형 (채택)</b></li>
                    <li><b>[임계 시나리오]</b> 한계치 (목표: {limit_val}) → 통계적 불확실성 과다 구간</li>
                </ul>
            </div>
            
            

            <div class="logic-card">
                <h5 style="color: #2B6CB0; margin-top:0;">2️⃣ 목표 도전성 분석 방법론 및 비교 입증</h5>
                <b>- 분석 기법:</b> 표준편차 기반 <b>Sigma Threshold 분석</b> 및 <b>선형 회귀 시계열 전망</b> 활용<br>
                <b>- 비교 입증:</b> 보수적 비교안 대비 약 <b>{round(abs(recom['최고목표']-compare_target['최고목표']), 3)}포인트</b>를 추가 확보함. 
                이는 단순 상향이 아닌, 조직의 잠재 역량을 최대한 끌어내야 달성 가능한 <b>'Stretch Goal'</b>임을 증명합니다.
            </div>

            <div class="logic-card">
                <h5 style="color: #2B6CB0; margin-top:0;">3️⃣ 평가위원 질의대응 방어 논리 (Defense Logic)</h5>
                <b>질문: "왜 더 높은 한계 시나리오를 선택하지 않았나?"</b><br>
                <b>답변:</b> "한계 시나리오는 통계적 예측 범위를 벗어난 이상치 구간으로, 무리한 설정 시 지표의 <b>변별력</b>이 상실될 리스크가 큽니다. 
                따라서 본 제안안은 <b>'도전성'</b>과 <b>'달성 가능성'</b>이 교차하는 최적의 지점(Optimal Point)을 산출한 결과입니다."
            </div>

            <div style="margin-top: 25px; padding: 15px; background-color: #E2E8F0; border-radius: 5px;">
                <b style="color: #2D3748;">📝 보고서 인용 예시 문구:</b><br>
                <i style="color: #4A5568;">"본 보고서는 <b>시나리오 기법</b>을 적용하여 성과 목표의 정당성을 검증하였음. 
                과거 5개년 실적의 변동성을 고려한 <b>[{recom['평가방법']}]</b> 모델을 통해 전년 대비 {diff_pct}% {direction_txt}된 도전적 목표를 설정하였으며, 
                이는 데이터 분석에 기반한 객관적 성과 관리 체계를 구축한 결과임."</i>
            </div>
        </div>
        """, unsafe_allow_html=True)
