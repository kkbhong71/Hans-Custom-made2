# 🎰 Han's Custom Made - 로또 예측 웹앱

통계 기반 로또 번호 예측 시스템입니다.  
7가지 알고리즘을 사용하여 당첨 확률이 높은 번호 조합을 추천합니다.

## 📸 스크린샷

![메인 화면](https://via.placeholder.com/800x400?text=Han's+Custom+Made)

## ✨ 주요 기능

- **7가지 예측 알고리즘**
  - 🎲 랜덤: Hot Pool 내 완전 랜덤
  - 📊 가중치: 빈도 기반 확률 선택
  - ⚖️ 밸런스: 홀짝 비율 최적화
  - 🎯 합계구간: 100~170 범위 유지
  - 🔀 패턴분산: 구간 집중 방지
  - 🌟 AI초정밀: 모든 조건 충족
  - 🛡️ 과적합방지: Cold 번호 혼합

- **실시간 분석**
  - Hot/Cold Pool 분류
  - 번호 빈도 차트
  - 다중 구간 분석 (30/50/100회차)

- **통계 지표**
  - AC값 (산술적 복잡도)
  - 홀짝/고저 비율
  - 끝수 합계
  - 구간 분포

## 🚀 빠른 시작

### 로컬 실행

```bash
# 1. 저장소 클론
git clone https://github.com/kkbhong71/Hans-Custom-made2.git
cd Hans-Custom-made2

# 2. 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 앱 실행
python app.py
```

브라우저에서 `http://localhost:5000` 접속

### Render.com 배포

1. GitHub에 저장소 푸시
2. [Render.com](https://render.com) 접속 → New Web Service
3. GitHub 저장소 연결
4. 설정:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Deploy 클릭

## 📁 프로젝트 구조

```
Hans-Custom-made2/
├── app.py                 # Flask 메인 앱
├── lotto_algorithm.py     # 예측 알고리즘 모듈
├── requirements.txt       # 패키지 목록
├── README.md              # 프로젝트 설명
├── templates/
│   └── index.html         # 웹 인터페이스
├── static/
│   └── style.css          # 스타일시트
└── data/
    └── new_1206.csv       # 당첨번호 데이터
```

## 🔌 API 엔드포인트

| 경로 | 메서드 | 설명 |
|------|--------|------|
| `/` | GET | 메인 페이지 |
| `/api/predict?window=50` | GET | 단일 구간 예측 |
| `/api/predict/multi` | GET | 다중 구간 예측 |
| `/api/info` | GET | 데이터 정보 |
| `/api/algorithm/<code>` | GET | 알고리즘 설명 |

## 📊 알고리즘 상세

### F타입: AI 초정밀 (완벽주의자)

모든 통계 조건을 충족하는 조합만 선택:

1. ✅ 합계: 100~170
2. ✅ 홀짝: 2:4 ~ 4:2
3. ✅ 고저: 2:4 ~ 4:2
4. ✅ AC값: 7 이상
5. ✅ 끝수합: 15~35
6. ✅ 3연번 제외

### G타입: 과적합 방지 (하이브리드)

Hot 번호에만 의존하지 않고 Cold 번호도 혼합:

- Hot 4개 + Cold 2개
- Hot 5개 + Cold 1개

## ⚠️ 주의사항

- 본 시스템은 **참고용**이며 당첨을 보장하지 않습니다.
- 로또는 완전한 확률 게임입니다.
- 과도한 도박은 건강에 해롭습니다.

## 📜 라이선스

MIT License

## 👤 제작자

- **kkbhong71**
- GitHub: [@kkbhong71](https://github.com/kkbhong71)

---

Made with ❤️ for 🎰 Lotto Prediction
