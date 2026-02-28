import math

def calculate_evaluation():
    print("=== 경영평가 계량지표 예상평점 산출 프로그램 ===")
    
    # 1. 기본 정보 입력
    indicator_name = input("지표명을 입력하세요: ")
    weight = float(input("가중치를 입력하세요 (예: 5.0): "))
    direction = input("지표 방향을 입력하세요 (상향/하향): ")
    
    # 2. 과거 실적 입력 (5개년)
    history = []
    for i in range(5, 0, -1):
        val = float(input(f"{i}년 전(Y-{i}) 실적을 입력하세요: "))
        history.append(val)
    
    current_estimated = float(input("당해연도 예상실적을 입력하세요: "))

    # 3. 기초 통계 계산
    last_3_avg = sum(history[-3:]) / 3
    # 편람 기준 표준편차 (n으로 나눔) [cite: 31]
    mean_history = sum(history) / 5
    variance = sum((x - mean_history) ** 2 for x in history) / 5
    std_dev = math.sqrt(variance)
    
    # 기준치 결정 (상향은 max, 하향은 min) 
    if direction == "상향":
        base_value = max(history[-1], last_3_avg)
    else:
        base_value = min(history[-1], last_3_avg)

    # 4. 평가방법별 시뮬레이션 [cite: 15, 20, 21, 22, 23, 24]
    def get_score(actual, high, low):
        if high == low: return 20.0
        score = 20 + 80 * (actual - low) / (high - low)
        return max(20.0, min(100.0, score))

    # [A] 일반 목표부여 (주요사업 120%/80% 적용) [cite: 21]
    if direction == "상향":
        goal_hi_gen, goal_lo_gen = base_value * 1.2, base_value * 0.8
    else:
        goal_hi_gen, goal_lo_gen = base_value * 0.8, base_value * 1.2
    
    score_gen = get_score(current_estimated, goal_hi_gen, goal_lo_gen)

    # [B] 목표부여(편차) (주요사업 2*표준편차 적용) [cite: 23, 24]
    if direction == "상향":
        goal_hi_dev, goal_lo_dev = base_value + 2 * std_dev, base_value - 2 * std_dev
    else:
        goal_hi_dev, goal_lo_dev = base_value - 2 * std_dev, base_value + 2 * std_dev
    
    score_dev = get_score(current_estimated, goal_hi_dev, goal_lo_dev)

    # 5. 결과 출력
    print(f"\n--- [{indicator_name}] 평가 결과 요약 ---")
    print(f"기준치: {base_value:.2f} | 표준편차: {std_dev:.2f}")
    print("-" * 40)
    print(f"[방법 A] 일반 목표부여 평점: {score_gen:.2f}점")
    print(f" (최고: {goal_hi_gen:.2f}, 최저: {goal_lo_gen:.2f})")
    print("-" * 40)
    print(f"[방법 B] 목표부여(편차) 평점: {score_dev:.2f}점")
    print(f" (최고: {goal_hi_dev:.2f}, 최저: {goal_lo_dev:.2f})")
    print("-" * 40)
    
    best_score = max(score_gen, score_dev)
    print(f"★ 유리한 방법: {'목표부여(편차)' if score_dev > score_gen else '일반 목표부여'}")
    print(f"★ 예상 득점(가중치 반영): {best_score * weight / 100:.3f}점")

    # 6. 향후 3개년 기준치 추정 (단순 롤링)
    print("\n--- 향후 3개년 기준치 추정 (예상실적 달성 가정) ---")
    current_rolling = history + [current_estimated]
    for year in range(1, 4):
        next_3_avg = sum(current_rolling[-3:]) / 3
        if direction == "상향":
            next_base = max(current_rolling[-1], next_3_avg)
        else:
            next_base = min(current_rolling[-1], next_3_avg)
        print(f"Y+{year} 예상 기준치: {next_base:.2f}")
        current_rolling.append(next_base) # 다음 연도도 기준치만큼 달성한다고 가정

if __name__ == "__main__":
    calculate_evaluation()
