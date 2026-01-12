"""
🎰 Han's Custom Made 로또 예측 알고리즘 모듈
==============================================
- 7가지 알고리즘 기반 번호 생성
- 통계적 분석 및 필터링
- 과적합 방지 로직 포함
"""

import pandas as pd
import numpy as np
import random
from itertools import combinations
from collections import Counter
from pathlib import Path


class LottoAnalyzer:
    """
    로또 번호 분석 및 예측 클래스
    
    Attributes:
        df: 당첨번호 데이터프레임
        number_cols: 번호 컬럼명 리스트
    """
    
    def __init__(self, csv_path=None):
        """
        초기화 메서드
        
        Args:
            csv_path: CSV 파일 경로 (None이면 기본 경로 사용)
        """
        if csv_path is None:
            # 기본 경로: 프로젝트 내 data 폴더
            base_dir = Path(__file__).parent
            csv_path = base_dir / 'data' / 'new_1206.csv'
        
        self.df = self._load_data(csv_path)
        self.number_cols = [f'num{i}' for i in range(1, 7)]
    
    def _load_data(self, path):
        """데이터 로드 및 정렬"""
        try:
            df = pd.read_csv(path)
            if 'round' in df.columns:
                df = df.sort_values(by='round', ascending=False).reset_index(drop=True)
            return df
        except Exception as e:
            print(f"❌ 파일 오류: {e}")
            return pd.DataFrame()
    
    def get_latest_round(self):
        """최신 회차 번호 반환"""
        if not self.df.empty and 'round' in self.df.columns:
            return int(self.df['round'].iloc[0])
        return 0
    
    # =========================================================
    # 통계 분석 유틸리티 함수들
    # =========================================================
    
    @staticmethod
    def calculate_ac_value(numbers):
        """
        AC(산술적 복잡도) 값 계산
        
        AC값이란?
        - 6개 번호에서 만들 수 있는 모든 차이값의 개수 - 5
        - 15개 조합에서 중복 제거 후 개수 계산
        - 7 이상이면 좋은 조합으로 평가
        
        Args:
            numbers: 6개 번호 리스트
        Returns:
            int: AC 값 (0~10 범위)
        """
        diffs = set()
        for a, b in combinations(numbers, 2):
            diffs.add(abs(a - b))
        return len(diffs) - 5
    
    @staticmethod
    def get_high_low_ratio(numbers):
        """
        고저(High/Low) 비율 계산
        
        기준: 22 이하 = Low, 23 이상 = High
        이상적 비율: 3:3 또는 2:4, 4:2
        
        Args:
            numbers: 6개 번호 리스트
        Returns:
            tuple: (low_count, high_count)
        """
        low = sum(1 for n in numbers if n <= 22)
        high = 6 - low
        return low, high
    
    @staticmethod
    def analyze_last_digit(numbers):
        """
        끝수(일의 자리) 분석
        
        검증 조건:
        1. 끝수 합계: 15~35 범위
        2. 동일 끝수 3개 이상 제외 (트리플 방지)
        
        Args:
            numbers: 6개 번호 리스트
        Returns:
            tuple: (통과여부, 끝수합계)
        """
        last_digits = [n % 10 for n in numbers]
        s_last = sum(last_digits)
        
        # 1. 끝수 합 검증
        if not (15 <= s_last <= 35):
            return False, s_last
        
        # 2. 트리플 방지
        counts = Counter(last_digits)
        if max(counts.values()) >= 3:
            return False, s_last
        
        return True, s_last
    
    @staticmethod
    def analyze_section_pattern(numbers):
        """
        구간별 분포 분석
        
        구간 정의:
        - 1~10: 1번대
        - 11~20: 10번대
        - 21~30: 20번대
        - 31~40: 30번대
        - 41~45: 40번대
        
        Args:
            numbers: 6개 번호 리스트
        Returns:
            list: 각 구간별 개수 [5개 요소]
        """
        sections = [0] * 5
        for n in numbers:
            if 1 <= n <= 10: sections[0] += 1
            elif 11 <= n <= 20: sections[1] += 1
            elif 21 <= n <= 30: sections[2] += 1
            elif 31 <= n <= 40: sections[3] += 1
            else: sections[4] += 1
        return sections
    
    @staticmethod
    def get_ball_color(number):
        """
        로또공 색상 반환 (웹 표시용)
        
        Args:
            number: 번호 (1~45)
        Returns:
            str: HEX 색상 코드
        """
        if 1 <= number <= 10: return '#FBC400'   # 노랑
        elif 11 <= number <= 20: return '#69C8F2'  # 파랑
        elif 21 <= number <= 30: return '#FF7272'  # 빨강
        elif 31 <= number <= 40: return '#AAAAAA'  # 회색
        else: return '#B0D840'  # 초록
    
    # =========================================================
    # 번호 생성 알고리즘
    # =========================================================
    
    def _pick_random(self, pool, k=6):
        """풀에서 랜덤하게 k개 선택"""
        return sorted(random.sample(pool, k))
    
    def _has_consecutive_three(self, numbers):
        """3연번 포함 여부 확인"""
        for i in range(len(numbers) - 2):
            if numbers[i+1] == numbers[i] + 1 and numbers[i+2] == numbers[i] + 2:
                return True
        return False
    
    def generate_numbers(self, algo_type, hot_pool, cold_pool, weights):
        """
        알고리즘별 번호 생성
        
        Args:
            algo_type: 알고리즘 코드 (A~G)
            hot_pool: 핫 넘버 리스트
            cold_pool: 콜드 넘버 리스트
            weights: 핫 넘버별 가중치
        Returns:
            list: 생성된 6개 번호
        """
        pool = hot_pool
        if len(pool) < 6:
            return []
        
        # [A] 랜덤 (Hot Pool 내)
        if algo_type == 'A':
            return self._pick_random(pool)
        
        # [B] 가중치 (자주 나온 번호 우대)
        elif algo_type == 'B':
            try:
                probs = np.array(weights) / sum(weights)
                sel = np.random.choice(pool, 6, replace=False, p=probs)
                return sorted([int(n) for n in sel])
            except:
                return self._pick_random(pool)
        
        # [C] 홀짝 밸런스 (2:4 ~ 4:2)
        elif algo_type == 'C':
            for _ in range(500):
                cand = self._pick_random(pool)
                odd = sum(1 for n in cand if n % 2 != 0)
                if 2 <= odd <= 4:
                    return cand
            return self._pick_random(pool)
        
        # [D] 합계 구간 (100~170)
        elif algo_type == 'D':
            for _ in range(500):
                cand = self._pick_random(pool)
                if 100 <= sum(cand) <= 170:
                    return cand
            return self._pick_random(pool)
        
        # [E] 패턴 분산 (구간 집중 방지 + 3연번 제외)
        elif algo_type == 'E':
            for _ in range(500):
                cand = self._pick_random(pool)
                sec = self.analyze_section_pattern(cand)
                if max(sec) >= 5:
                    continue
                if not self._has_consecutive_three(cand):
                    return cand
            return self._pick_random(pool)
        
        # [F] 🔥 AI 초정밀 (완벽주의자) - 모든 조건 충족
        elif algo_type == 'F':
            for _ in range(10000):
                cand = self._pick_random(pool)
                
                # 1. 합계 검증 (100~170)
                if not (100 <= sum(cand) <= 170):
                    continue
                # 2. 홀짝 검증 (2:4 ~ 4:2)
                odd = sum(1 for n in cand if n % 2 != 0)
                if not (2 <= odd <= 4):
                    continue
                # 3. 고저 검증 (2:4 ~ 4:2)
                low, high = self.get_high_low_ratio(cand)
                if not (2 <= low <= 4):
                    continue
                # 4. AC값 검증 (>= 7)
                if self.calculate_ac_value(cand) < 7:
                    continue
                # 5. 끝수 검증
                valid_last, _ = self.analyze_last_digit(cand)
                if not valid_last:
                    continue
                # 6. 3연번 제외
                if self._has_consecutive_three(cand):
                    continue
                
                return cand
            
            # 실패 시 조건 완화
            for _ in range(1000):
                cand = self._pick_random(pool)
                if 100 <= sum(cand) <= 170:
                    return cand
            return self._pick_random(pool)
        
        # [G] 🛡️ 과적합 방지 (Hot + Cold 혼합)
        elif algo_type == 'G':
            if len(cold_pool) < 2:
                return sorted(random.sample(hot_pool + cold_pool, 6))
            
            for _ in range(2000):
                # 혼합 비율: (Hot 4 : Cold 2) 또는 (Hot 5 : Cold 1)
                mix_ratio = random.choice([(4, 2), (5, 1)])
                n_hot, n_cold = mix_ratio
                
                try:
                    part1 = random.sample(hot_pool, n_hot)
                    part2 = random.sample(cold_pool, n_cold)
                except:
                    continue
                
                cand = sorted(part1 + part2)
                
                # 기본 필터
                if not (80 <= sum(cand) <= 200):
                    continue
                if not self._has_consecutive_three(cand):
                    return cand
            
            return sorted(random.sample(hot_pool + cold_pool, 6))
        
        return self._pick_random(pool)
    
    # =========================================================
    # 메인 분석 및 예측 메서드
    # =========================================================
    
    def analyze_and_predict(self, window=50):
        """
        메인 분석 및 예측 수행
        
        Args:
            window: 분석 구간 (최근 N회차)
        Returns:
            dict: 분석 결과 및 예측 번호
        """
        if self.df.empty:
            return {"error": "데이터가 없습니다."}
        
        # 1. 데이터 집계
        df_numbers = self.df[self.number_cols]
        subset = df_numbers.head(window)
        counts = pd.Series(subset.values.flatten()).value_counts().sort_index()
        
        # 2. Hot / Cold 분류
        hot_mask = counts >= 2
        hot_target = counts[hot_mask]
        
        hot_pool = hot_target.index.tolist()
        weights = hot_target.values.tolist()
        cold_pool = [n for n in range(1, 46) if n not in hot_pool]
        
        # 3. 번호 생성
        algo_list = [
            ('A', '랜덤'),
            ('B', '가중치'),
            ('C', '밸런스'),
            ('D', '합계구간'),
            ('E', '패턴분산'),
            ('F', 'AI초정밀'),
            ('G', '과적합방지')
        ]
        
        predictions = []
        for code, name in algo_list:
            nums = self.generate_numbers(code, hot_pool, cold_pool, weights)
            if not nums:
                continue
            
            # 상세 정보 계산
            section = self.analyze_section_pattern(nums)
            ac_value = self.calculate_ac_value(nums)
            valid_last, last_sum = self.analyze_last_digit(nums)
            low, high = self.get_high_low_ratio(nums)
            odd = sum(1 for n in nums if n % 2 != 0)
            
            # 콜드 번호 개수 (G 알고리즘용)
            cold_count = sum(1 for n in nums if n in cold_pool)
            
            predictions.append({
                "code": code,
                "name": name,
                "numbers": nums,
                "colors": [self.get_ball_color(n) for n in nums],
                "sum": sum(nums),
                "section": section,
                "ac_value": ac_value,
                "last_digit_sum": last_sum,
                "odd_even": f"{odd}:{6-odd}",
                "high_low": f"{low}:{high}",
                "cold_count": cold_count
            })
        
        # 4. Hot Pool 빈도 데이터 (차트용)
        frequency_data = {
            "numbers": hot_pool,
            "counts": weights,
            "colors": [self.get_ball_color(n) for n in hot_pool]
        }
        
        # 5. 결과 반환
        return {
            "latest_round": self.get_latest_round(),
            "window": window,
            "hot_pool_size": len(hot_pool),
            "cold_pool_size": len(cold_pool),
            "hot_pool": hot_pool,
            "cold_pool": cold_pool,
            "predictions": predictions,
            "frequency_data": frequency_data
        }
    
    def get_multi_window_results(self, windows=[30, 50, 100]):
        """
        여러 구간에 대한 분석 결과 반환
        
        Args:
            windows: 분석 구간 리스트
        Returns:
            dict: 구간별 분석 결과
        """
        results = {}
        for w in windows:
            results[w] = self.analyze_and_predict(window=w)
        return results


# 테스트용 코드
if __name__ == "__main__":
    analyzer = LottoAnalyzer()
    result = analyzer.analyze_and_predict(window=50)
    
    print(f"📊 최신 회차: {result['latest_round']}")
    print(f"🔥 Hot Pool: {result['hot_pool_size']}개")
    print(f"❄️ Cold Pool: {result['cold_pool_size']}개")
    print("\n[예측 번호]")
    for pred in result['predictions']:
        print(f"  [{pred['code']}] {pred['name']}: {pred['numbers']}")
