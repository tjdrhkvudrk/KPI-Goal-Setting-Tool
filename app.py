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
    .sb-title { font-size: 16px !important; font-weight: 800 !important; color: #1A202C; margin-top: 15px; margin-bottom: 5px; display: block; }
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label, div[data-testid="stRadio"] > label { display: none !important; }
    .auto-res { background-color: #F8FAFC; border: 1px solid #dee2e6; height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .guide-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; line-height: 1.8; }
    .recom-box { background-color: #FFF5F5; border: 1px solid #E53E3E; border-radius: 10px; padding: 20px; margin-top: 15px; border-left: 5px solid #E53E3E; }
    .guide-title { font-weight: bold; color: #2D3748; font-size: 16px; margin-bottom: 10px; display: block; }
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; }
    thead tr th:first-child, tbody tr th { display: none; }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바
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

# 실적 분석 안내
avg3, std3 = round(np.mean(실적_리스트[-3:]), 3), round(np.std(실적_리스트[-3:]), 3)
st.markdown(f"""
<div class="guide-box">
    <span class="guide-title">📑 실적 분석 참고내용</span>
    • <b>과거 3개년 실적 분석결과:</b> 평균 {avg3:.3f}, 표준편차 {std3:.3f}, 연평균 증가율 {round(((실적_리스트[-1]/실적_리스트[-3])**(1/2)-1)*100, 3):.3f}%<br>
    • <b>중장기 전망 분석결과:</b> 평균 {round(np.mean(미래_전망), 3):.3f}, 연평균 증가율 {round(((미래_전망[-1]/예상_2026)**(1/3)-1)*100, 3):.3f}%
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if st.button("🚀 중장기 성과 및 한계점 분석 실행"):
    # 분석 로직 계산
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
    final_title = display_name if display_name != "미설정 지표" else "지표"
    st.subheader(f"2. {final_title} - 평가방법별 비교 분석 결과 및 임계점 진단")
    df_res = pd.DataFrame(결과_데이터)
    st.table(df_res.drop(columns=['raw_도전성']).style.format({col: "{:.3f}" for col in ["기준치", "최저목표", "최고목표", "예상실적", "예상평점", "가중치", "예상득점"]}))

    # --- [위치 이동] 분석 지표 가이드 (표 바로 아래) ---
    st.markdown("""
    <div class="guide-box">
        <span class="guide-title">💡 분석 지표 가이드</span>
        <b>1. 도전성 단계 분석 (과거 추세 대비 상향 정도)</b><br>
        • 🏆 <b>한계 혁신</b>: 목표치가 예상 실적보다 표준편차의 3배 이상 높은 경우로, 과거의 흐름을 완전히 벗어난 파격적 목표 수준<br>
        • 🔥 <b>적극 상향</b>: 목표치가 과거 변동폭의 1.6배~3배 수준으로, 과거 성장세를 상회하는 공격적 목표 수준<br>
        • 📈 <b>소극 개선</b>: 목표치가 과거 변동 범위 내에 존재하며, 과거의 완만한 우상향 추세를 따르는 안정적 수준<br>
        • ⚖️ <b>현상 유지</b>: 목표치가 예상 실적과 유사하거나 과거 평균 수준에 머무르는 경우로, 과거 실적 평균 수준의 관리 중심 목표 수준<br><br>
        <b>2. 추세치 분석결과 (한계 판정 기준)</b><br>
        • ⚠️ <b>한계</b>: 목표치가 과거 표준편차의 3배를 초과하거나 30% 이상 급변하여 역량상 임계점에 도달했음을 의미합니다.
    </div>
    """, unsafe_allow_html=True)

    # --- 3. 그래프 시뮬레이션 ---
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

    # --- 4. 담당자 보고용 최적 목표 제안 ---
    st.subheader("4. 담당자 보고용 최적 목표 제안 및 논리적 근거")
    유지가능 = [d for d in 결과_데이터 if d['추세치 분석결과'] == "✅ 유지"]
    
    if 유지가능:
        recom = max(유지가능, key=lambda x: x['raw_도전성'])
        lower_options = sorted(유지가능, key=lambda x: x['raw_도전성'])
        alternative = lower_options[0] if len(lower_options) > 1 else None
        diff_percent = abs(round((recom['최고목표'] / 예상_2026 - 1) * 100, 2))
        
        compare_text = ""
        if alternative and alternative['평가방법'] != recom['평가방법']:
            compare_text = f"기존의 <b>[{alternative['평가방법']}]</b> 등 보수적인 설정 방식도 검토하였으나, 성과 창출 동기 부여를 위해 <b>이보다 목표 수준이 더 높은 [{recom['평가방법']}]</b>을 최종 최적안으로 선정하였습니다."
        else:
            compare_text = "다각적인 시뮬레이션을 통해 단순 개선을 넘어선 <b>가장 도전적인 수준의 목표 부여 방식</b>을 채택하였습니다."

        st.markdown(f"""
        <div class="recom-box">
            <span class="guide-title" style="color:#C53030;">🎯 추천 시나리오: [{recom['평가방법']}] 적용 (도전적 목표 채택)</span>
            <b>• 제안 목표치:</b> {recom['최고목표']:.3f} (예상 실적 대비 {diff_percent}% {"상향" if 지표방향=="상향" else "하향"} 설정)<br>
            <b>• 도전성 단계:</b> {recom['도전성 단계']}<br><br>
            <b>[보고서용 논리적 근거 초안]</b><br>
            1. <b>도전적 목표 설정의 적극성:</b> {compare_text} 이는 과거의 성과를 단순히 답습하는 것이 아니라, 잠재 역량을 최대한으로 이끌어내야 달성 가능한 <b>'Stretch Goal'</b> 성격의 수치입니다.<br>
            2. <b>통계적 타당성 기반의 상향 설정:</b> 본 안은 과거 변동 패턴 내에서 <b>통계적으로 수용 가능한 가장 높은 수준</b>을 지향합니다. 단순히 무리한 수치를 제시하는 것이 아니라, 과거 실적의 표준편차를 정밀 분석하여 '근거 있는 상향'을 도출함으로써 목표의 정당성을 확보하였습니다.<br>
            3. <b>실현 가능한 한계치(Boundary) 확보:</b> 역량상의 임계점(3-Sigma)을 넘지 않는 범위 내에서 최고치를 설정함으로써, <b>도전성은 극대화하되 달성 가능성은 포기하지 않는</b> 최적의 균형점을 찾았습니다.<br>
            4. <b>미래 성장성 반영:</b> 예측 모델이 제시하는 중장기 전망치보다 높은 목표 설정을 통해, 대내외에 혁신적인 성과 창출 의지를 표명하고 조직의 지속적인 성장을 견인하고자 합니다.
        </div>
        """, unsafe_allow_html=True)
