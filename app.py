import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# ──────────────────────────────────────────────
# 1. 한글 폰트 설정
# ──────────────────────────────────────────────
@st.cache_resource
def load_korean_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
    font_path = "NanumGothic-Bold.ttf"
    if not os.path.exists(font_path):
        try:
            res = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(res.content)
        except:
            pass
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
        plt.rc('axes', unicode_minus=False)
        return font_path
    plt.rc('axes', unicode_minus=False)
    return None

_font_file = load_korean_font()
font_prop = fm.FontProperties(fname=_font_file) if _font_file else None

# ──────────────────────────────────────────────
# 2. 페이지 설정 & CSS
# ──────────────────────────────────────────────
st.set_page_config(page_title="계량 성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; font-family: 'NanumGothic', sans-serif; }
    .sidebar-label { font-size: 16px; font-weight: 800; color: #1A202C; margin-top: 15px; margin-bottom: 8px; display: block; }
    .sidebar-white-box { background-color: white; border-radius: 8px; padding: 12px; border: 1px solid #E2E8F0; margin-bottom: 5px; }
    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stRadio"] > label { display: none !important; }
    .main-header { padding: 10px; color: white; text-align: center; font-weight: bold; margin-bottom: 5px; border-radius: 5px 5px 0 0; }
    .bg-past    { background-color: #2D6A4F; }
    .bg-current { background-color: #D69E2E; }
    .bg-future  { background-color: #4A5568; }
    .sub-header { background-color: #f1f3f5; padding: 5px; text-align: center; font-size: 13px; font-weight: bold; border: 1px solid #dee2e6; border-top: none; }
    .auto-res   { background-color: #F8FAFC; border: 1px solid #dee2e6; height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .guide-box  { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; line-height: 1.8; }
    .strong-label { font-size: 20px !important; font-weight: 900 !important; color: #1A365D !important; margin-bottom: 12px; display: block; }

    /* 도전성 단계 배지 — 한 줄 가로 배치 */
    .step-bar { display: flex; gap: 10px; margin: 14px 0 4px 0; flex-wrap: wrap; }
    .step-chip { border-radius: 8px; padding: 10px 16px; border-left: 5px solid; background-color: #FFFFFF;
                 box-shadow: 0 2px 4px rgba(0,0,0,0.06); flex: 1; min-width: 180px; }
    .step-chip .chip-title { font-weight: bold; font-size: 15.5px; }
    .step-chip .chip-desc  { font-size: 13px; color: #4A5568; margin-top: 4px; }
    .chip-1 { border-left-color: #E53E3E; } .chip-2 { border-left-color: #DD6B20; }
    .chip-3 { border-left-color: #38A169; } .chip-4 { border-left-color: #A0AEC0; }

    .formula-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; background-color: white; }
    .formula-table th { border: 1px solid #E2E8F0; padding: 8px; text-align: center !important; }
    .formula-table td { border: 1px solid #E2E8F0; padding: 8px; text-align: left !important; }
    .up-col   { background-color: #EBF8FF !important; color: #2B6CB0 !important; }
    .down-col { background-color: #FFF5F5 !important; color: #C53030 !important; }

    .cmp-table { width: 100%; border-collapse: collapse; font-size: 13.5px; margin-top: 8px; }
    .cmp-table th { background-color: #4A5568; color: white; text-align: center; border: 1px solid #CBD5E0; padding: 8px 6px; white-space: nowrap; }
    .cmp-table td { text-align: center; vertical-align: middle; border: 1px solid #E2E8F0; padding: 7px 5px; }
    .cmp-table .merged-cell  { background-color: #EDF2F7; font-weight: bold; color: #2D3748; }
    .cmp-table .merged-cell2 { background-color: #EBF8FF; font-weight: bold; color: #2B6CB0; }
    .th-low  { background-color: #3182CE !important; }
    .th-high { background-color: #C53030 !important; }
    .th-real { background-color: #276749 !important; }
    .col-high { color: #C53030; font-weight: bold; }
    .col-low  { color: #2B6CB0; font-weight: bold; }
    .col-real { color: #276749; font-weight: bold; }

    .valid-card   { background-color: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .status-badge { padding: 4px 12px; border-radius: 15px; font-weight: bold; font-size: 14px; margin-bottom: 10px; display: inline-block; }
    .status-ok    { background-color: #C6F6D5; color: #22543D; }
    .status-warn  { background-color: #FED7D7; color: #822727; }

    .draft-box { background-color: #FFFBEB; border: 1.5px solid #F6AD55; border-radius: 12px; padding: 22px 26px; line-height: 2.0; color: #2D3748; font-size: 14.5px; margin-top: 12px; }
    .draft-box .draft-title { font-size: 16px; font-weight: bold; color: #7B341E; margin-bottom: 14px; display: block; }
    .draft-box .draft-para  { margin-bottom: 14px; }
    .draft-box .hl { background-color: #FEF3C7; padding: 1px 5px; border-radius: 4px; font-weight: bold; }

    /* 섹션 헤더 스타일 */
    .section-header { background: linear-gradient(90deg, #2D3748 0%, #4A5568 100%);
                      color: white; padding: 10px 18px; border-radius: 8px;
                      font-size: 16px; font-weight: bold; margin: 18px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 3. 사이드바
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="sidebar-label">📌 지표명</span>', unsafe_allow_html=True)
    지표명 = st.text_input("kpi_name", value="전략 KPI", label_visibility="collapsed")
    st.markdown('<span class="sidebar-label">🎯 지표 성격</span>', unsafe_allow_html=True)
    지표방향 = st.radio("direction", ["상향", "하향"], horizontal=True, label_visibility="collapsed")
    st.markdown('<span class="sidebar-label">⚖️ 가중치</span>', unsafe_allow_html=True)
    가중치_값 = st.number_input("weight", value=5.000, step=0.001, format="%.3f", label_visibility="collapsed")

st.title("📊 계량 성과지표 목표 설정 및 중장기 전망 시뮬레이터")

# ──────────────────────────────────────────────
# SECTION 1. 실적 데이터 입력 및 분석
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">1. 실적 데이터 입력 및 분석</div>', unsafe_allow_html=True)

실적_리스트 = []
m_cols = st.columns([4.8, 1.6, 3.2])

with m_cols[0]:
    st.markdown('<div class="main-header bg-past">과거 5개년 실적 (2021~2025)</div>', unsafe_allow_html=True)
    p_cols = st.columns(5)
    for i, year in enumerate(range(2021, 2026)):
        with p_cols[i]:
            st.markdown(f'<div class="sub-header">{year}</div>', unsafe_allow_html=True)
            val = st.number_input(f"p_{year}", value=round(100.0 + i * 5, 3),
                                  step=0.001, format="%.3f", key=f"v_{year}")
            실적_리스트.append(val)

유효_실적 = [v for v in 실적_리스트 if v != 0]
n유효 = len(유효_실적)

X_past = np.arange(5)
Y_past = np.array(실적_리스트)
slope_p, intercept_p = np.polyfit(X_past, Y_past, 1)
suggested_2026 = round(slope_p * 5 + intercept_p, 3)

with m_cols[1]:
    st.markdown('<div class="main-header bg-current">2026년 (예상)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header" style="font-size:12.5px;">추세 기반 자동입력 (수정 가능)</div>', unsafe_allow_html=True)
    예상_2026 = st.number_input("curr_2026", value=suggested_2026,
                                 step=0.001, format="%.3f", key="v_2026")

with m_cols[2]:
    st.markdown('<div class="main-header bg-future">중장기 실적 전망 (자동)</div>', unsafe_allow_html=True)
    f_cols = st.columns(3)
    X_full = np.arange(6)
    Y_full = np.array(실적_리스트 + [예상_2026])
    slope_f, intercept_f = np.polyfit(X_full, Y_full, 1)
    미래_전망 = []
    for i, year in enumerate(range(2027, 2030)):
        with f_cols[i]:
            st.markdown(f'<div class="sub-header">{year}</div>', unsafe_allow_html=True)
            f_val = round(slope_f * (6 + i) + intercept_f, 3)
            미래_전망.append(f_val)
            st.markdown(f'<div class="auto-res">{f_val:.3f}</div>', unsafe_allow_html=True)

# ── 통계 계산 ──
avg3  = round(np.mean(실적_리스트[-3:]), 3)
std3  = round(np.std(실적_리스트[-3:]), 3)
cagr3 = round(((실적_리스트[-1] / 실적_리스트[-3]) ** (1/2) - 1) * 100, 3) if 실적_리스트[-3] != 0 else 0

avg5  = round(np.mean(실적_리스트), 3)
std5  = round(np.std(실적_리스트), 3)
cagr5 = round(((실적_리스트[-1] / 실적_리스트[0]) ** (1/4) - 1) * 100, 3) if 실적_리스트[0] != 0 else 0

전망_전체 = [예상_2026] + 미래_전망
avg_f  = round(np.mean(전망_전체), 3)
std_f  = round(np.std(전망_전체), 3)
cagr_f = round(((미래_전망[-1] / 예상_2026) ** (1/3) - 1) * 100, 3) if 예상_2026 != 0 else 0

std_for_target = std5 if n유효 >= 5 else std3
std_구간 = "5개년" if n유효 >= 5 else "3개년"

# ── 실적 분석 참고내용: 바로 표시 ──
st.markdown(f"""
<div class="guide-box">
    <span style="font-weight:bold; color:#2D3748;">📑 실적 분석 참고내용</span><br>
    • <b>과거 3개년 실적 분석결과 (2023~2025):</b> 평균 {avg3:.3f}, 표준편차 {std3:.3f}, 연평균 증가율 {cagr3:.3f}%<br>
    • <b>과거 5개년 실적 분석결과 (2021~2025):</b> 평균 {avg5:.3f}, 표준편차 {std5:.3f}, 연평균 증가율 {cagr5:.3f}%<br>
    • <b>중장기 전망 분석결과 (2026~2029):</b> 평균 {avg_f:.3f}, 표준편차 {std_f:.3f}, 연평균 증가율 {cagr_f:.3f}%
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ──────────────────────────────────────────────
# SECTION 2. 평가방법별 목표 도전성 비교
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">2. 평가방법별 목표 도전성 비교</div>', unsafe_allow_html=True)

if 지표방향 == "상향":
    기준치 = round(float(max(avg3, 실적_리스트[-1])), 3)
else:
    기준치 = round(float(min(avg3, 실적_리스트[-1])), 3)

s = std_for_target
추세_2026 = round(slope_f * 6 + intercept_f, 3)


def calc_high_low(방법명):
    if 지표방향 == "상향":
        if 방법명 == "목표부여(2편차)":
            return round(기준치 + 2*s, 3), round(기준치 - 2*s, 3)
        elif 방법명 == "목표부여(1편차)":
            return round(기준치 + 1*s, 3), round(기준치 - 2*s, 3)
        elif 방법명 == "목표부여(120%)":
            return round(기준치 * 1.2, 3), round(기준치 * 0.8, 3)
        elif 방법명 == "목표부여(110%)":
            return round(기준치 * 1.1, 3), round(기준치 * 0.8, 3)
        elif 방법명 == "낙관적 시나리오":
            return round(추세_2026 + s * 1.5, 3), round(추세_2026 - s * 1.5, 3)
        elif 방법명 == "기본 시나리오":
            return round(추세_2026, 3), round(추세_2026 - s, 3)
        else:
            return round(추세_2026 - s * 1.0, 3), round(추세_2026 - s * 2.0, 3)
    else:
        if 방법명 == "목표부여(2편차)":
            return round(기준치 - 2*s, 3), round(기준치 + 2*s, 3)
        elif 방법명 == "목표부여(1편차)":
            return round(기준치 - 1*s, 3), round(기준치 + 2*s, 3)
        elif 방법명 == "목표부여(120%)":
            return round(기준치 * 0.8, 3), round(기준치 * 1.2, 3)
        elif 방법명 == "목표부여(110%)":
            return round(기준치 * 0.9, 3), round(기준치 * 1.2, 3)
        elif 방법명 == "낙관적 시나리오":
            return round(추세_2026 - s * 1.5, 3), round(추세_2026 + s * 1.5, 3)
        elif 방법명 == "기본 시나리오":
            return round(추세_2026, 3), round(추세_2026 + s, 3)
        else:
            return round(추세_2026 + s * 1.0, 3), round(추세_2026 + s * 2.0, 3)


def calc_score(최고목표, 최저목표, 예상실적):
    if 지표방향 == "상향":
        분자 = 예상실적 - 최저목표
    else:
        분자 = 최저목표 - 예상실적
    denom = abs(최고목표 - 최저목표) if 최고목표 != 최저목표 else 1
    return round(max(20.0, min(100.0, 20 + 80 * (분자 / denom))), 3)


방법명_리스트 = [
    ("목표부여",      "목표부여(2편차)"),
    ("목표부여",      "목표부여(1편차)"),
    ("목표부여",      "목표부여(120%)"),
    ("목표부여",      "목표부여(110%)"),
    ("시나리오 분석", "낙관적 시나리오"),
    ("시나리오 분석", "기본 시나리오"),
    ("시나리오 분석", "보수적 시나리오"),
]

결과_데이터 = []
for 분류, 명칭 in 방법명_리스트:
    최고목표, 최저목표 = calc_high_low(명칭)
    예상평점 = calc_score(최고목표, 최저목표, 예상_2026)
    예상득점 = round(예상평점 * (가중치_값 / 100.0), 3)

    오차 = max(abs(최고목표 - 최저목표) * 0.5, 0.001)
    if 지표방향 == "상향":
        도전성_지수 = round(((최고목표 - 예상_2026) / 오차) * 100, 3)
    else:
        도전성_지수 = round(((예상_2026 - 최고목표) / 오차) * 100, 3)

    단계 = ("🏆 한계 혁신" if 도전성_지수 >= 150 else
            "🔥 적극 상향" if 도전성_지수 >= 80  else
            "📈 소극 개선" if 도전성_지수 >= 40  else
            "⚖️ 현상 유지")
    판정 = ("✅ 유지" if (abs(최고목표 - 기준치) <= 3 * std3 and
                         abs(최고목표 / 기준치 - 1) <= 0.3) else "⚠️ 한계")

    결과_데이터.append({
        "구분":       분류,
        "평가방법":   명칭,
        "기준치":     기준치,
        "최저목표":   최저목표,
        "최고목표":   최고목표,
        "예상실적":   예상_2026,
        "예상평점":   예상평점,
        "가중치":     가중치_값,
        "예상득점":   예상득점,
        "도전성 단계": 단계,
        "분석결과":   판정,
    })

# ── 도전성 비교 테이블 ──
def td(val, cls=""):
    cls_str = f' class="{cls}"' if cls else ""
    if isinstance(val, float):
        return f"<td{cls_str}>{val:.3f}</td>"
    return f"<td{cls_str}>{val}</td>"

rows_html = ""
for i, r in enumerate(결과_데이터):
    if i == 0:
        구분_td = '<td rowspan="4" class="merged-cell">목표부여</td>'
    elif i == 4:
        구분_td = '<td rowspan="3" class="merged-cell merged-cell2">시나리오 분석</td>'
    else:
        구분_td = ""
    border_style = ' style="border-top:2px solid #4A5568;"' if i == 4 else ""
    row = (f'<tr{border_style}>' + 구분_td
           + f'<td>{r["평가방법"]}</td>'
           + td(r["기준치"])
           + td(r["최저목표"], "col-low")
           + td(r["최고목표"], "col-high")
           + td(r["예상실적"], "col-real")
           + td(r["예상평점"])
           + td(r["가중치"])
           + td(r["예상득점"])
           + f'<td>{r["도전성 단계"]}</td>'
           + f'<td>{r["분석결과"]}</td>'
           + "</tr>")
    rows_html += row

html_table = f"""
<table class="cmp-table">
    <thead>
        <tr>
            <th>구분</th>
            <th>평가방법</th>
            <th>기준치</th>
            <th class="th-low">최저목표</th>
            <th class="th-high">최고목표</th>
            <th class="th-real">예상실적</th>
            <th>예상평점</th>
            <th>가중치</th>
            <th>예상득점</th>
            <th>도전성 단계</th>
            <th>분석결과</th>
        </tr>
    </thead>
    <tbody>{rows_html}</tbody>
</table>
"""
st.markdown(html_table, unsafe_allow_html=True)

# ── 도전성 판정기준 — 표 바로 아래 가로 배치 ──
st.markdown("""
<div style="margin-top: 14px; margin-bottom: 4px; font-size: 13px; font-weight: bold; color: #4A5568;">
    💡 도전성 단계 판정기준
</div>
<div class="step-bar">
    <div class="step-chip chip-1">
        <div class="chip-title" style="color:#E53E3E;">🏆 한계 혁신</div>
        <div class="chip-desc">추세선 대비 1.5σ 초과<br>혁신적 방법을 동원해야 달성 가능한 최상위 목표</div>
    </div>
    <div class="step-chip chip-2">
        <div class="chip-title" style="color:#DD6B20;">🔥 적극 상향</div>
        <div class="chip-desc">추세선 대비 1.0~1.5σ<br>업무 프로세스 개선 및 추가 자원 투입이 필요한 수준</div>
    </div>
    <div class="step-chip chip-3">
        <div class="chip-title" style="color:#38A169;">📈 소극 개선</div>
        <div class="chip-desc">통계적 변동성 범위 내 (0.4~1.0σ)<br>자연 성장 추세를 반영한 현실적 목표</div>
    </div>
    <div class="step-chip chip-4">
        <div class="chip-title" style="color:#718096;">⚖️ 현상 유지</div>
        <div class="chip-desc">0.4σ 미만<br>최근 실적 유지 또는 보수적 목표 설정</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 산식 가이드: HTML details/summary 태그로 접기/펼치기 ──
st.markdown(f"""
<details style="margin-top:10px; background-color:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px 16px;">
  <summary style="cursor:pointer; list-style:none; display:flex; align-items:center; gap:8px;">
    <span style="font-size:18px;">📋</span>
    <span style="font-weight:bold; font-size:15px; color:#2D3748;">평가방법별 목표 산식 및 설명 (상향/하향 비교 가이드)</span>
    <span style="font-size:13.5px; color:#718096; font-weight:normal; margin-left:8px;">* 클릭하면 상세한 설명을 확인하실 수 있습니다</span>
  </summary>
  <div style="margin-top:10px;">
    <span style="font-size:12px; color:#718096;">※ 표준편차(std)는 과거 {std_구간} 실적 기준 {std_for_target:.3f} 적용</span>
    <table class="formula-table" style="margin-top:8px;">
        <thead>
            <tr>
                <th rowspan="2" style="background-color:#F7FAFC; width:13%;">평가방법</th>
                <th colspan="3" class="up-col">📈 상향 지표 (실적이 높을수록 우수)</th>
                <th colspan="3" class="down-col">📉 하향 지표 (실적이 낮을수록 우수)</th>
            </tr>
            <tr>
                <th class="up-col">최고목표</th><th class="up-col">최저목표</th><th class="up-col">설명</th>
                <th class="down-col">최고목표</th><th class="down-col">최저목표</th><th class="down-col">설명</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="font-weight:bold; text-align:center !important;">목표부여(2편차)</td>
                <td>기준치 <b>+ 2×std</b></td><td>기준치 <b>- 2×std</b></td><td>변동폭 2배 도전</td>
                <td>기준치 <b>- 2×std</b></td><td>기준치 <b>+ 2×std</b></td><td>변동폭 2배 감축 도전</td>
            </tr>
            <tr>
                <td style="font-weight:bold; text-align:center !important;">목표부여(1편차)</td>
                <td>기준치 <b>+ 1×std</b></td><td>기준치 <b>- 2×std</b></td><td>1표준편차 상향</td>
                <td>기준치 <b>- 1×std</b></td><td>기준치 <b>+ 2×std</b></td><td>1표준편차 하향</td>
            </tr>
            <tr>
                <td style="font-weight:bold; text-align:center !important;">목표부여(120%)</td>
                <td>기준치 <b>× 1.2</b></td><td>기준치 <b>× 0.8</b></td><td>20% 절대 증가</td>
                <td>기준치 <b>× 0.8</b></td><td>기준치 <b>× 1.2</b></td><td>20% 절대 감축</td>
            </tr>
            <tr>
                <td style="font-weight:bold; text-align:center !important;">목표부여(110%)</td>
                <td>기준치 <b>× 1.1</b></td><td>기준치 <b>× 0.8</b></td><td>10% 점진적 증가</td>
                <td>기준치 <b>× 0.9</b></td><td>기준치 <b>× 1.2</b></td><td>10% 점진적 감축</td>
            </tr>
            <tr>
                <td style="font-weight:bold; text-align:center !important;">낙관적 시나리오</td>
                <td>추세선 <b>+ 1.5×std</b></td><td>추세선 <b>- 1.5×std</b></td><td>혁신 가중치 반영</td>
                <td>추세선 <b>- 1.5×std</b></td><td>추세선 <b>+ 1.5×std</b></td><td>혁신 감축 반영</td>
            </tr>
            <tr>
                <td style="font-weight:bold; text-align:center !important;">기본 시나리오</td>
                <td>추세선</td><td>추세선 <b>- 1×std</b></td><td>추세 중립</td>
                <td>추세선</td><td>추세선 <b>+ 1×std</b></td><td>추세 중립</td>
            </tr>
            <tr>
                <td style="font-weight:bold; text-align:center !important;">보수적 시나리오</td>
                <td>추세선 <b>- 1×std</b></td><td>추세선 <b>- 2×std</b></td><td>불확실성 반영 하한</td>
                <td>추세선 <b>+ 1×std</b></td><td>추세선 <b>+ 2×std</b></td><td>불확실성 반영 상한</td>
            </tr>
        </tbody>
    </table>
  </div>
</details>
""", unsafe_allow_html=True)

st.markdown("---")

# ──────────────────────────────────────────────
# SECTION 3. 중장기 추세 및 시나리오별 목표 궤적 분석
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">3. 중장기 추세 및 시나리오별 목표 궤적 분석</div>', unsafe_allow_html=True)

years_all_label = [f"'{y-2000}" for y in range(2021, 2030)]
idx_future = np.arange(6, 10)
base_trend = slope_f * idx_future + intercept_f

if 지표방향 == "상향":
    line_optimistic   = [예상_2026] + list(base_trend[1:] + std5 * 1.5)
    line_conservative = [예상_2026] + list(base_trend[1:] - std5 * 1.0)
else:
    line_optimistic   = [예상_2026] + list(base_trend[1:] - std5 * 1.5)
    line_conservative = [예상_2026] + list(base_trend[1:] + std5 * 1.0)
line_base = [예상_2026] + list(base_trend[1:])

fig, ax = plt.subplots(figsize=(13, 6.5))
ax.plot(years_all_label[:6], Y_full, marker='o', color='#2D3748', linewidth=3.5, label="과거 실적", zorder=20)
ax.scatter(years_all_label[5], 예상_2026, color='#F6E05E', s=250, marker='D',
           edgecolor='#2D3748', linewidth=2, label='2026 예상실적', zorder=25)
ax.plot(years_all_label[5:], line_optimistic,   color='#3182CE', linestyle='--', linewidth=2, label='낙관적 시나리오')
ax.plot(years_all_label[5:], line_base,          color='#718096', linestyle='--', linewidth=2, label='기본 시나리오')
ax.plot(years_all_label[5:], line_conservative,  color='#D69E2E', linestyle='--', linewidth=2, label='보수적 시나리오')

colors = ['#E53E3E', '#DD6B20', '#38A169', '#805AD5']
for i, row in enumerate(결과_데이터[:4]):
    ax.scatter(years_all_label[5], row['최고목표'], s=160, color=colors[i],
               label=f"{row['평가방법']} 최고목표", zorder=30, edgecolors='white', linewidth=1.5)

ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1, 1), frameon=True, shadow=True)
ax.grid(axis='y', linestyle='-', alpha=0.1)
st.pyplot(fig)

st.markdown("---")

# ──────────────────────────────────────────────
# SECTION 4. 도전적 목표 설정 가이드 (담당자 제언)
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">4. 도전적 목표 설정 가이드 (담당자 제언)</div>', unsafe_allow_html=True)

if 'f_idx' not in st.session_state:
    st.session_state.f_idx = 0
names = [r['평가방법'] for r in 결과_데이터]
compare_names = ["기준치"] + names

col_a, col_b = st.columns(2)
with col_a:
    st.markdown('<span class="strong-label">🎯 담당자 최종 선택 평가방법</span>', unsafe_allow_html=True)
    선택방법 = st.selectbox("final_select", names,
                             index=st.session_state.f_idx, key="box_f",
                             label_visibility="collapsed")
    st.session_state.f_idx = names.index(선택방법)
with col_b:
    st.markdown('<span class="strong-label">⚖️ 비교 대상 (대조군)</span>', unsafe_allow_html=True)
    비교방법 = st.selectbox("compare_select", compare_names,
                             index=0, key="box_c", label_visibility="collapsed")

sel = next(item for item in 결과_데이터 if item["평가방법"] == 선택방법)

# 타당성 배지
st.markdown('<span style="font-weight: bold; font-size: 16px; color: #1A365D;">🔍 목표 설정 타당성 검토 결과</span>', unsafe_allow_html=True)
status_class = "status-ok" if sel['분석결과'] == "✅ 유지" else "status-warn"
판정_설명 = ("통계적으로 달성 가능한 범위 안에 있어, <b>과거 실적의 자연스러운 성장 추세를 반영한 합리적인 목표</b>입니다." if sel['분석결과'] == "✅ 유지"
             else "과거 실적 변동폭을 크게 벗어난 수치로, <b>기존 방식으로는 달성이 어려운 혁신적 목표</b>임을 평가위원에게 별도로 설명하는 것이 좋습니다.")
st.markdown(f"""
<div class="valid-card">
    <div class="status-badge {status_class}">{sel['분석결과']}</div>
    <div style="font-size: 14.5px; color: #2D3748;">
        선택하신 최고목표 <b>{sel['최고목표']:.3f}</b>는 {판정_설명}
    </div>
</div>
""", unsafe_allow_html=True)

# ── 원고 초안 — 탭으로 분리 ──
방향_텍스트 = "높일수록" if 지표방향 == "상향" else "낮출수록"

if 지표방향 == "상향":
    if 실적_리스트[-1] >= avg3:
        기준치_근거 = f"직전년도(2025년) 실적({실적_리스트[-1]:.3f})이 과거 3개년 평균({avg3:.3f})보다 높아 직전년도 실적을 기준치로 채택"
    else:
        기준치_근거 = f"과거 3개년 평균({avg3:.3f})이 직전년도(2025년) 실적({실적_리스트[-1]:.3f})보다 높아 3개년 평균을 기준치로 채택"
else:
    if 실적_리스트[-1] <= avg3:
        기준치_근거 = f"직전년도(2025년) 실적({실적_리스트[-1]:.3f})이 과거 3개년 평균({avg3:.3f})보다 낮아(개선된) 직전년도 실적을 기준치로 채택"
    else:
        기준치_근거 = f"과거 3개년 평균({avg3:.3f})이 직전년도(2025년) 실적({실적_리스트[-1]:.3f})보다 낮아(더 좋아) 3개년 평균을 기준치로 채택"

if 비교방법 == "기준치":
    gap_val  = round(abs(sel['최고목표'] - 기준치), 3)
    gap_rate = round((gap_val / 기준치) * 100, 2) if 기준치 != 0 else 0
    비교_문장 = (f"기준치({기준치:.3f})보다 {gap_val}({gap_rate}%) "
                f"{'높게' if 지표방향 == '상향' else '낮게'} 최고목표를 설정하였습니다.")
else:
    comp = next(item for item in 결과_데이터 if item["평가방법"] == 비교방법)
    gap_val = round(abs(sel['최고목표'] - comp['최고목표']), 3)
    비교_문장 = (f"다른 산출 방식인 '{비교방법}'({comp['최고목표']:.3f})보다 {gap_val} "
                f"{'높은' if 지표방향 == '상향' else '낮은'} 수준으로 더 도전적인 목표를 채택하였습니다.")

단계_설명_dict = {
    "🏆 한계 혁신": (
        "이는 현재 조직이 보유한 인력·예산·시스템만으로는 달성하기 매우 어려운, "
        "최대한의 노력과 혁신적인 방법을 동원해야만 가능한 최상위 목표 수준입니다. "
        "조직이 한 단계 도약하겠다는 강한 의지를 담은 목표라고 볼 수 있습니다."
    ),
    "🔥 적극 상향": (
        "이는 현재 방식을 그대로 유지해서는 달성하기 어렵고, "
        "업무 프로세스 개선이나 추가적인 자원 투입이 필요한 도전적 목표 수준입니다. "
        "단순 현상 유지가 아닌 실질적인 성과 향상을 지향하고 있습니다."
    ),
    "📈 소극 개선": (
        "이는 과거 실적의 자연스러운 성장 추세를 반영하면서, "
        "무리하지 않고 현실적으로 달성 가능한 범위에서 개선을 추구하는 목표입니다. "
        "안정적이면서도 성과 향상을 놓치지 않는 균형 잡힌 목표입니다."
    ),
    "⚖️ 현상 유지": (
        "이는 최근 실적 수준을 유지하거나 소폭 개선하는 것을 목표로 한 것으로, "
        "급격한 변화보다는 안정적인 성과 관리에 초점을 두고 있습니다."
    ),
}
단계_한글 = sel['도전성 단계']
단계_부연 = 단계_설명_dict.get(단계_한글, "")

평점 = sel['예상평점']
if 평점 >= 90:
    평점_해석 = f"예상 평점은 <span class='hl'>{평점:.1f}점</span>으로, 현재 예상실적 수준에서도 최고 등급에 가까운 성과를 인정받을 가능성이 높습니다."
elif 평점 >= 70:
    평점_해석 = f"예상 평점은 <span class='hl'>{평점:.1f}점</span>으로, 현재 예상실적 기준 평균 이상의 양호한 성과 등급을 받을 것으로 예상됩니다."
elif 평점 >= 50:
    평점_해석 = f"예상 평점은 <span class='hl'>{평점:.1f}점</span>으로, 현재 예상실적 기준 보통 수준의 성과로 평가받을 것으로 보이며, 실적 향상 시 점수 상승 여지가 있습니다."
else:
    평점_해석 = f"예상 평점은 <span class='hl'>{평점:.1f}점</span>으로, 예상실적이 목표 구간 하단에 위치하고 있어 실적 개선 노력이 중요합니다."


hl = lambda text: f'<span class="hl">{text}</span>'

draft_html = (
    '<div class="draft-box">'
    '<span class="draft-title">📝 평가위원 설명용 원고 초안 — 이 내용을 그대로 발표·보고서에 활용하실 수 있습니다</span>'

    '<div class="draft-para">'
    '<b>① 이 지표가 무엇인지, 어떤 의미인지</b><br>'
    + f'저희가 이번에 목표를 설정한 지표는 <span class="hl">「{지표명}」</span>입니다. '
    + f'이 지표는 수치가 <span class="hl">{방향_텍스트}</span> 좋은 평가를 받는 지표이며, '
    + f'전체 평가에서 <span class="hl">{가중치_값:.1f}점</span>의 가중치를 차지하는 중요한 항목입니다.'
    + '</div>'

    + '<div class="draft-para">'
    + '<b>② 목표를 세우는 출발점(기준치)을 어떻게 정했는지</b><br>'
    + f'목표 수준을 정하기 위한 출발점인 기준치는 <span class="hl">{기준치:.3f}</span>로 설정하였습니다. '
    + f'이는 {기준치_근거}한 것입니다. '
    + '이렇게 기준치를 높게(또는 엄격하게) 잡음으로써, 목표가 과거 실적보다 후퇴하는 일이 없도록 하였습니다.'
    + '</div>'

    + '<div class="draft-para">'
    + '<b>③ 어떤 방식으로 목표 수치를 계산했는지</b><br>'
    + f'목표 산출 방식으로는 <span class="hl">「{선택방법}」</span>을 선택하였습니다. '
    + f'이 방식은 과거 {std_구간} 실적 데이터의 통계적 변동 폭(표준편차 {std_for_target:.3f})과 실적 추세를 함께 반영하여 목표 구간을 설정하는 방법입니다.<br>'
    + f'이에 따라 최고목표는 <span class="hl">{sel["최고목표"]:.3f}</span>, '
    + f'최저목표는 <span class="hl">{sel["최저목표"]:.3f}</span>로 설정되었으며, '
    + 비교_문장
    + '</div>'

    + '<div class="draft-para">'
    + '<b>④ 이 목표가 얼마나 도전적인지</b><br>'
    + f'설정된 목표는 도전성 분석 결과 <span class="hl">{단계_한글}</span>으로 판정되었습니다. '
    + 단계_부연 + '<br>'
    + f'2026년 예상실적({예상_2026:.3f}) 기준으로 평가하면, '
    + 평점_해석
    + f' 가중치({가중치_값:.1f}점)를 반영한 예상 득점은 <span class="hl">{sel["예상득점"]:.3f}점</span>입니다.'
    + '</div>'

    + '<div class="draft-para">'
    + '<b>⑤ 중장기적으로 지속 가능한 목표인지</b><br>'
    + f'과거 5개년 실적 추세를 바탕으로 분석한 결과, 2027~2029년의 연평균 증가율은 <span class="hl">{cagr_f:.3f}%</span>로 전망됩니다. '
    + '본 목표는 이러한 중장기 성장 방향과 일관성을 유지하고 있으며, '
    + '지속적인 관리와 개선 노력을 병행한다면 충분히 달성 가능한 수준이라고 판단하였습니다.'
    + '</div>'
    + '</div>'
)
st.markdown(draft_html, unsafe_allow_html=True)
