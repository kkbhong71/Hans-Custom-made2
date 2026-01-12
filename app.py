"""
🌐 Han's Custom Made 로또 예측 웹앱
=====================================
Flask 기반 웹 애플리케이션
- 메인 페이지 라우팅
- API 엔드포인트 제공
- JSON 응답 처리
"""

from flask import Flask, render_template, jsonify, request
from lotto_algorithm import LottoAnalyzer
import os

# =========================================================
# Flask 앱 초기화
# =========================================================
app = Flask(__name__)

# 분석기 인스턴스 생성 (앱 시작 시 1회만 로드)
analyzer = LottoAnalyzer()


# =========================================================
# 라우트 정의
# =========================================================

@app.route('/')
def index():
    """
    메인 페이지 렌더링
    
    Templates:
        index.html: 메인 웹 인터페이스
    """
    latest_round = analyzer.get_latest_round()
    return render_template('index.html', latest_round=latest_round)


@app.route('/api/predict', methods=['GET'])
def predict():
    """
    예측 API 엔드포인트
    
    Query Parameters:
        window (int): 분석 구간 (기본값: 50)
    
    Returns:
        JSON: 예측 결과
        {
            "latest_round": 1207,
            "window": 50,
            "hot_pool_size": 32,
            "cold_pool_size": 13,
            "predictions": [...],
            "frequency_data": {...}
        }
    
    Example:
        GET /api/predict?window=30
        GET /api/predict?window=100
    """
    try:
        # 쿼리 파라미터에서 window 값 추출 (기본값 50)
        window = request.args.get('window', default=50, type=int)
        
        # 유효 범위 검증 (10 ~ 500)
        if window < 10:
            window = 10
        elif window > 500:
            window = 500
        
        # 분석 실행
        result = analyzer.analyze_and_predict(window=window)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/predict/multi', methods=['GET'])
def predict_multi():
    """
    다중 구간 예측 API
    
    기본 구간: 30, 50, 100회차
    
    Returns:
        JSON: 구간별 예측 결과
    """
    try:
        results = analyzer.get_multi_window_results(windows=[30, 50, 100])
        
        return jsonify({
            "success": True,
            "data": results
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/info', methods=['GET'])
def get_info():
    """
    데이터 정보 API
    
    Returns:
        JSON: 데이터셋 기본 정보
    """
    try:
        latest_round = analyzer.get_latest_round()
        total_records = len(analyzer.df)
        
        # 최근 5회차 당첨번호
        recent_numbers = []
        for i in range(min(5, total_records)):
            row = analyzer.df.iloc[i]
            numbers = [int(row[f'num{j}']) for j in range(1, 7)]
            recent_numbers.append({
                "round": int(row['round']),
                "date": str(row['draw date']),
                "numbers": numbers,
                "colors": [analyzer.get_ball_color(n) for n in numbers]
            })
        
        return jsonify({
            "success": True,
            "data": {
                "latest_round": latest_round,
                "total_records": total_records,
                "recent_numbers": recent_numbers
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/algorithm/<algo_code>', methods=['GET'])
def get_algorithm_detail(algo_code):
    """
    특정 알고리즘 상세 정보 API
    
    Path Parameters:
        algo_code: 알고리즘 코드 (A~G)
    
    Returns:
        JSON: 알고리즘 설명 및 샘플 번호
    """
    algo_info = {
        'A': {
            'name': '랜덤',
            'description': 'Hot Pool(최근 2회 이상 등장 번호)에서 완전 랜덤 선택',
            'strength': '예측 불가능성',
            'icon': '🎲'
        },
        'B': {
            'name': '가중치',
            'description': '자주 등장한 번호에 높은 확률 부여하여 선택',
            'strength': '빈도 기반 분석',
            'icon': '📊'
        },
        'C': {
            'name': '밸런스',
            'description': '홀수/짝수 비율을 2:4 ~ 4:2로 유지',
            'strength': '홀짝 균형',
            'icon': '⚖️'
        },
        'D': {
            'name': '합계구간',
            'description': '6개 번호 합계를 100~170 범위로 제한',
            'strength': '합계 통계 기반',
            'icon': '🎯'
        },
        'E': {
            'name': '패턴분산',
            'description': '특정 구간 집중 방지 + 3연번 제외',
            'strength': '분포 균등화',
            'icon': '🔀'
        },
        'F': {
            'name': 'AI초정밀',
            'description': '합계, 홀짝, 고저, AC값, 끝수, 연번 모든 조건 충족',
            'strength': '완벽한 통계적 조합',
            'icon': '🌟'
        },
        'G': {
            'name': '과적합방지',
            'description': 'Hot 번호와 Cold 번호를 혼합하여 의외성 확보',
            'strength': '데이터 편향 방지',
            'icon': '🛡️'
        }
    }
    
    algo_code = algo_code.upper()
    
    if algo_code not in algo_info:
        return jsonify({
            "success": False,
            "error": "유효하지 않은 알고리즘 코드입니다. (A~G)"
        }), 400
    
    return jsonify({
        "success": True,
        "data": algo_info[algo_code]
    })


# =========================================================
# 에러 핸들러
# =========================================================

@app.errorhandler(404)
def not_found(e):
    """404 에러 핸들러"""
    return jsonify({
        "success": False,
        "error": "요청한 페이지를 찾을 수 없습니다."
    }), 404


@app.errorhandler(500)
def server_error(e):
    """500 에러 핸들러"""
    return jsonify({
        "success": False,
        "error": "서버 내부 오류가 발생했습니다."
    }), 500


# =========================================================
# 앱 실행
# =========================================================

if __name__ == '__main__':
    # 개발 모드에서는 debug=True
    # 배포 시에는 Gunicorn이 실행하므로 이 블록은 무시됨
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
