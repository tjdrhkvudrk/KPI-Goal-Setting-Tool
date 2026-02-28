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

# 2. CSS 디자인 (이미지처럼 태그가 보이지 않도록 깔끔하게 렌더링)
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; font-family: 'NanumGothic', sans-serif; }
    .main-header { padding: 10px; color: white; text-align: center; font-weight: bold; margin-bottom: 5px; border-radius: 5px 5px 0 0; }
    .bg-past { background-color: #2D6A4F; }
    .bg-current { background-color: #D69E2E; }
    .bg-future { background-color: #4A5568; }
    .sub-header { background-color: #f1f3f5; padding: 5px; text-align: center; font-size: 13px; font-weight: bold; border: 1px solid #dee2e6; border-top: none; }
    
    /* 카드형 가이드 스타일 */
    .summary-card { background-color: #EBF8FF; border-left: 8px solid #2B6CB0; border-radius: 10px; padding: 25px; margin-bottom: 20px; }
    .detail-card { background-color: #F7FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 25px; margin-top: 15px; }
    .logic-inner { background-color: white; border: 1px solid #CBD5E0; border-radius: 8px; padding: 18px; margin-top: 15px; line-height: 1.8; }
    .guide-title { font-weight: bold; color: #2C5282; font-size: 18px; margin-bottom: 15px; display: block; }
    
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바 설정
with st.sidebar:
    st.header("📊 지표 설정")
    지표명 = st.text_input("지표명을 입력하세요", value="지표명")
    지표방향 = st.radio("목표 방향", ["상향", "하향"], horizontal=True)
    가중치_값 = st.number_input("가중치", value=5.000, step=0.001, format="%.3f")

# --- 1. 데이터 입력 및 상세 통계 (완벽 복구) ---
st.subheader("1. 실적 데이터 및 중장기 전망")
실적_리스트 = []
m_cols = st.columns([5, 1, 3])

with m_cols[0]:
    st.markdown('<div class="main-header bg-past">과거 5개년 실적 (2021~2025)</div>', unsafe_allow_html=True)
    p_cols = st.columns(5)
    for i, year in enumerate(range(2021, 2026)):
        with p_cols[i]:
            val = st.number_input(f"{year}", value=round(100.0 + (i*5), 3), step=0.001, format="%.3f")
            실적_리스트.append(val)

with m_cols[1]:
    st.markdown('<div class="main-header bg-current">2026년 예상</div>', unsafe_allow_html=True)
    예상_2026 = st.number_input("2026 실적", value=round(실적_리스트[-1] * 1.05, 3), step=0.001, format="%.3f")

with m_cols[2]:
    st.markdown('<div class="main-header bg-future">중장기 실적 전망</div>', unsafe_allow_html=True)
    f_cols = st.columns(3)
    X, Y = np.arange(6), np.array(실적_리스트 + [예상_2026])
    slope, intercept = np.polyfit(X, Y, 1)
    미래_전망 = []
    for i, year in enumerate(range(2027, 2030)):
        with f_cols[i]:
            f_val = round(slope * (6 + i) + intercept, 3)
            미래_전망.append(f_val)
            st.markdown(f'<div class="sub-header">{year}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="auto-res">{f_val:.3f}</div>', unsafe_allow_html=True)

# 상세 통계 섹션 (완벽 복구)
avg3, std3 = round(np.mean(실적_리스트[-3:]), 3), round(np.std(실적_리스트[-3:]), 3)
avg5, std5 = round(np.mean(실적_리스트), 3), round(np.std(실적_리스트), 3)
cagr_f = round(((미래_전망[-1]/예상_2026)**(1/3)-1)*100, 3) if 예상_2026 != 0 else 0

st.markdown(f"""
<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 15px; margin-top: 10px;">
    <b>📑 [데이터 분석 요약]</b> 
    • <b>과거 3개년:</b> 평균 {avg3:.3f} / 표준편차 {std3:.3f} 
    • <b>과거 5개년:</b> 평균 {avg5:.3f} / 표준편차 {std5:.3f}
    • <b>향후 3년 전망:</b> 평균 {np.mean(미래_전망):.3f} / 연평균증가율(CAGR) {cagr_f:.3f}%
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if st.button("🚀 전체 분석 실행"):
    # 2. 결과 분석 로직
    기준치 = round(float(max(avg3, 실적_리스트[-1]) if 지표방향=="상향" else min(avg3, 실적_리스트[-1])), 3)
    방법별 = [("목표부여(2편차)", round(기준치 + 2*std3 if 지표방향=="상향" else 기준치 - 2*std3, 3)),
              ("목표부여(1편차)", round(기준치 + std3 if 지표방향=="상향" else 기준치 - std3, 3)),
              ("목표부여(120%)", round(기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8, 3)),
              ("목표부여(110%)", round(기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9, 3))]

    결과 = []
    오차 = max(np.std(Y), 기준치 * 0.1)
    for 명칭, 최고 in 방법별:
        최저 = round(기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2, 3)
        평점 = round(max(20.0, min(100.0, 20 + 80 * ((예상_2026 - 최저) / (최고 - 최저)))), 3)
        zp = (최고 - 예상_2026) / 오차 if 지표방향=="상향" else (예상_2026 - 최고) / 오차
        도전성_지수 = round((zp / 2.0) * 100, 3)
        단계 = "🏆 한계 혁신" if 도전성_지수 >= 150 else "🔥 적극 상향" if 도전성_지수 >= 80 else "📈 소극 개선" if 도전성_지수 >= 40 else "⚖️ 현상 유지"
        판정 = "⚠️ 한계" if (abs(최고 - 기준치) > (3 * std3) or abs(최고/기준치 - 1) > 0.3) else "✅ 유지"
        결과.append({"평가방법": 명칭, "최고목표": 최고, "예상득점": round(평점 * (가중치_값 / 100.0), 3), "도전성 단계": 단계, "추세치 분석결과": 판정, "raw": 도전성_지수})

    df = pd.DataFrame(결과)
    st.table(df.drop(columns=['raw']).style.format({col: "{:.3f}" for col in ["최고목표", "예상득점"]}))

    # 도전성 단계 설명 (완벽 복구)
    st.markdown("""
    <div style="background-color: #F8FAFC; padding: 15px; border-radius: 10px; font-size: 14px; border: 1px solid #E2E8F0;">
        <b>💡 도전성 단계 정의:</b> 
        🏆<b>한계 혁신</b>: 표준편차 3배 초과 | 🔥<b>적극 상향</b>: 과거 추세 상회 | 📈<b>소극 개선</b>: 변동 범위 내 | ⚖️<b>현상 유지</b>: 평균 수준
    </div>
    """, unsafe_allow_html=True)

    # 4. 시나리오 및 도전성 입증 가이드 (통합형)
    st.subheader("4. 최종 성과목표 제안 및 도전성 입증")
    유지가능 = [d for d in 결과 if d['추세치 분석결과'] == "✅ 유지"]
    
    if 유지가능:
        recom = max(유지가능, key=lambda x: x['raw'])
        consv = min(유지가능, key=lambda x: x['raw'])
        diff_pct = round(abs((recom['최고목표'] / 예상_2026 - 1) * 100), 2)

        # [Summary 박스]
        st.markdown(f"""
        <div class="summary-card">
            <span class="guide-title">🎯 [최종 제안] 성과목표 설정 시나리오 요약</span>
            본 지표는 <b>[{recom['평가방법']}]</b> 시나리오를 채택하여, 전년 실적 대비 <b>{diff_pct}% {"상향" if 지표방향=="상향" else "하향"}</b>된 
            <b>{recom['최고목표']:.3f}</b>를 최종 목표로 제안합니다. 이는 보수적 안({consv['최고목표']:.3f}) 대비 도전성을 대폭 강화한 수치입니다.
        </div>
        """, unsafe_allow_html=True)

        # [상세 입증 박스 - 태그 노출 해결]
        st.markdown(f"""
        <div class="detail-card">
            <span class="guide-title">🔍 목표 설정의 과학적 근거 및 도전성 입증</span>
            
            <div class="logic-inner">
                <b>1️⃣ 시나리오 기법 (Scenario Planning) 적용</b><br>
                • <b>보수 시나리오:</b> {consv['평가방법']} ({consv['최고목표']:.3f}) → 과거 추세 답습형<br>
                • <b>도전 시나리오:</b> {recom['평가방법']} ({recom['최고목표']:.3f}) → <b>역량 집중 및 성과 견인형 (채택)</b><br>
                • <b>임계 시나리오:</b> 한계 판정 기준 수치 → 통계적 불확실성 과다 구간
            </div>

            <div class="logic-inner">
                <b>2️⃣ 목표 도전성 분석 방법론 및 비교 입증</b><br>
                • <b>분석 기법:</b> 표준편차 기반 <b>Sigma Threshold 분석</b> 및 <b>회귀 분석 전망</b> 활용<br>
                • <b>비교 입증:</b> 보수적 대안 대비 약 <b>{round(abs(recom['최고목표']-consv['최고목표']), 3)}포인트</b>를 추가 확보함으로써, 
                단순 관행적 설정을 탈피한 실질적 <b>'Stretch Goal'</b>임을 증명함.
            </div>

            <div class="logic-inner">
                <b>3️⃣ 평가위원 질의대응 방어 논리 (Defense Logic)</b><br>
                • <b>질문:</b> "왜 더 높은 한계치를 설정하지 않았는가?"<br>
                • <b>답변:</b> "한계치를 초과하는 설정은 지표의 <b>변별력</b>을 상실시키고 달성 의욕을 저해할 리스크가 큼. 
                따라서 본 제안은 <b>도전성</b>과 <b>현실성</b>이 교차하는 최적의 지점(Optimal Point)을 산출한 것임."
            </div>

            <div style="margin-top: 20px; padding: 15px; background-color: #E2E8F0; border-radius: 5px; font-style: italic;">
                "본 보고서는 <b>시나리오 기법</b>을 적용하여 성과 목표의 정당성을 검증함. 과거 5개년 변동성을 반영한 [{recom['평가방법']}] 모델을 통해 
                전년 대비 {diff_pct}% 상향된 도전적 목표를 설정하였으며, 이는 객관적 데이터 기반의 성과 관리 체계를 실현한 결과임."
            </div>
        </div>
        """, unsafe_allow_html=True)
