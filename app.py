import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import pandas as pd
import numpy as np

# 1. 화면 스타일 및 서식
style = {'description_width': '150px'}
layout = widgets.Layout(width='500px')

# 2. 입력 위젯 구성
title = widgets.HTML("<h2>🎯 도전적 목표 설정 및 평점 시뮬레이터</h2>")
indicator_name = widgets.Text(description="지표명:", value="주요사업 성과지표", style=style, layout=layout)
weight = widgets.FloatText(description="가중치:", value=5.0, style=style)
direction = widgets.Dropdown(description="지표 방향:", options=['상향', '하향'], value='상향', style=style)

# 도전성 조절 슬라이더 (기준치 대비 목표를 얼마나 더 높게 잡을 것인가)
stretch_rate = widgets.FloatSlider(description="목표 도전율(%):", min=0, max=20, step=0.5, value=2.0, 
                                   style=style, layout=layout, help="기준치에 추가할 도전적 가산율입니다.")

# 과거 실적 입력 (5개년)
history_widgets = [widgets.FloatText(description=f"Y-{i} 실적:", value=100.0 + (5-i)*5, style=style) for i in range(5, 0, -1)]
current_estimated = widgets.FloatText(description="당해 예상실적:", value=125.0, style=style)

calc_button = widgets.Button(description="도전적 목표 시뮬레이션 실행", button_style='danger', layout={'width': '300px'})
output = widgets.Output()

# 3. 계산 및 시뮬레이션 함수
def run_simulation(_):
    with output:
        clear_output()
        
        # 값 추출
        name = indicator_name.value
        w = weight.value
        direct = direction.value
        stretch = stretch_rate.value / 100  # 퍼센트를 소수로 변환
        hist_vals = [wd.value for wd in history_widgets]
        est = current_estimated.value
        
        # 기본 통계량
        last_3_avg = sum(hist_vals[-3:]) / 3
        std_dev = np.std(hist_vals)
        
        # 1. 기초 기준치 산정
        if direct == "상향":
            raw_base = max(hist_vals[-1], last_3_avg)
            # 도전성 부여: 기준치 자체를 stretch만큼 상향 조정
            challenged_base = raw_base * (1 + stretch)
        else:
            raw_base = min(hist_vals[-1], last_3_avg)
            # 하향지표는 기준치를 stretch만큼 더 낮게 잡아야 도전적임
            challenged_base = raw_base * (1 - stretch)
            
        # 평점 계산 함수
        def calc_score(actual, hi, lo):
            if hi == lo: return 20.0
            s = 20 + 80 * (actual - lo) / (hi - lo)
            return max(20.0, min(100.0, s))

        # [방법 A] 일반 방식 (기준치 대비 +/- 20% 폭)
        hi_gen, lo_gen = (challenged_base * 1.2, challenged_base * 0.8) if direct == "상향" else (challenged_base * 0.8, challenged_base * 1.2)
        score_gen = calc_score(est, hi_gen, lo_gen)
        
        # [방법 B] 편차 방식 (기준치 대비 +/- 2*std_dev)
        hi_dev, lo_dev = (challenged_base + 2*std_dev, challenged_base - 2*std_dev) if direct == "상향" else (challenged_base - 2*std_dev, challenged_base + 2*std_dev)
        score_dev = calc_score(est, hi_dev, lo_dev)
        
        # 결과 표시
        display(HTML(f"<h3>📊 '{name}' 시뮬레이션 결과 (도전율 {stretch*100}%)</h3>"))
        display(HTML(f"<b>순수 기준치:</b> {raw_base:.2f} ➔ <b>도전적 기준치:</b> <span style='color:red'>{challenged_base:.2f}</span>"))
        
        res_df = pd.DataFrame({
            "항목": ["최고목표(S등급)", "최저목표(E등급)", "예상평점", "예상득점"],
            "일반 목표부여": [f"{hi_gen:.2f}", f"{lo_gen:.2f}", f"{score_gen:.2f}점", f"{score_gen*w/100:.3f}점"],
            "목표부여(편차)": [f"{hi_dev:.2f}", f"{lo_dev:.2f}", f"{score_dev:.2f}점", f"{score_dev*w/100:.3f}점"]
        })
        display(res_df)
        
        # 전략적 조언
        gap = abs(score_gen - score_dev)
        better = "편차 방식" if score_dev > score_gen else "일반 방식"
        display(HTML(f"<div style='border:1px solid #ddd; padding:10px; background:#f9f9f9;'>"
                     f"💡 <b>전략 조언:</b> 도전성을 {stretch*100}% 부여했을 때, <b>{better}</b>이 약 {gap:.2f}점 더 유리합니다.<br>"
                     f"목표가 도전적일수록 표준편차가 큰 지표는 '편차 방식'이 평점 방어에 유리할 수 있습니다.</div>"))

# 이벤트 연결 및 배치
calc_button.on_click(run_simulation)
ui = widgets.VBox([
    title,
    widgets.HTML("<b>1. 지표 기본정보 및 도전성 설정</b>"),
    indicator_name, widgets.HBox([weight, direction, stretch_rate]),
    widgets.HTML("<br><b>2. 과거 실적 및 올해 예상치</b>"),
    widgets.HBox(history_widgets[:3]), widgets.HBox(history_widgets[3:] + [current_estimated]),
    widgets.HTML("<br>"),
    calc_button
])

display(ui, output)
