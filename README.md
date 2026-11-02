# DataGuard

## 프로젝트 소개
DataGuard는 소규모 CSV 파일의 데이터 품질을 진단하고 수치형 데이터의 이상치를 탐지하는 로컬 웹서비스입니다. 업로드 파일은 메모리에서만 처리하며 서버에 저장하지 않습니다.

## 주요 기능
- CSV 업로드 및 형식 검증
- 행/컬럼 수, 자료형, 결측치, 중복 행 표시
- 수치형 컬럼 통계와 Isolation Forest 이상치 탐지
- 결과 카드, 표, 미리보기 대시보드
- 오류 입력에 대한 사용자 안내

## 사용 기술
Python, FastAPI, Pandas, Scikit-learn, HTML, CSS, JavaScript

## CSV 크기 및 행 수 제한
- 파일 크기: 최대 5MB
- 데이터 행 수: 최대 20,000행
- 미리보기: 최대 5,000행
- 이상치 탐지 수치형 컬럼: 최대 5개

## 설치 방법
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 실행 방법
```powershell
python -m uvicorn app:app --reload
```
브라우저에서 `http://127.0.0.1:8000`을 엽니다.

## 지원하지 않는 입력
CSV가 아닌 파일, 5MB 초과 파일, 20,000행 초과 파일은 지원하지 않습니다. 빈 파일, 컬럼이 없는 파일, 손상된 CSV, UTF-8로 읽을 수 없는 CSV도 분석하지 않습니다. 오류 발생 시 서버를 중단하지 않고 안내 메시지를 표시합니다.

## 이상치 탐지 방식
수치형 컬럼이 있으면 결측치와 무한값을 제외한 데이터에 Scikit-learn의 `IsolationForest`를 적용합니다. 메모리 사용량 제한을 위해 최대 5개 수치형 컬럼만 사용하며 이상치 개수와 비율을 표시합니다. 수치형 컬럼이 없거나 분석 가능한 행이 부족하면 건너뜁니다.

## 향후 개선점
- CSV 인코딩 자동 감지 및 다양한 구분자 지원
- 컬럼별 분포와 이상치 시각화
- 결과 JSON/CSV 다운로드
- 구조화된 로깅과 세분화된 API 상태 코드
- 분석 이력 관리 기능
