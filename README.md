# 올리브영 실시간 랭킹 데이터 파이프라인 구축

![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat&logo=selenium&logoColor=white)
![PostgreSQL](https://img_shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/status-active-success)

## 📖 프로젝트 개요

올리브영 웹사이트의 실시간 상품 랭킹 데이터를 수집, 정제, 저장하고 API를 통해 제공하는 완전한 데이터 파이프라인 구축을 목표로 합니다.

- **`Crawl`**: Selenium과 BeautifulSoup을 사용하여 동적 웹 페이지에서 데이터를 수집합니다.
- **`Clean`**: 수집된 Raw 데이터를 число 형식 변환, 정규 표현식 적용 등 일관된 형식으로 정제합니다.
- **`Store`**: 정제된 데이터를 PostgreSQL 데이터베이스에 안정적으로 저장합니다.
- **`Serve`** : FastAPI를 사용하여 저장된 데이터를 외부에 제공하는 REST API를 구축합니다.

---

## 🛠️ 기술 스택

- **언어**: Python
- **웹 크롤링**: Selenium, BeautifulSoup4
- **데이터베이스**: PostgreSQL
- **API 서버**: FastAPI, Uvicorn
- **의존성 관리**: requirements.txt

---

## ⚙️ 실행 방법

### 1. 사전 준비

- Python 3.10+ 설치
- PostgreSQL 서버 설치 및 실행

### 2. 프로젝트 설정

```bash
# 1. 프로젝트 클론
git clone https://github.com/your-username/oliveyoung-crawler.git
cd oliveyoung-crawler

# 2. 파이썬 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 필요한 라이브러리 설치
pip install -r requirements.txt

# 4. 데이터베이스 설정
# db_config.py 파일을 생성하고 아래와 같이 본인의 PostgreSQL 접속 정보를 입력합니다.
# (이 파일은 .gitignore에 등록하여 민감한 정보가 노출되지 않도록 합니다.)
```

**`db_config.py`**
```python
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "oliveyoung_db", # 생성한 DB 이름
    "user": "your_username",     # PostgreSQL 사용자 이름
    "password": "your_password"  # PostgreSQL 비밀번호
}
```

### 3. 파이프라인 실행

**1. 데이터 수집 및 저장 (Crawl, Clean, Store)**
```bash
# 아래 명령어를 실행하면 크롤러가 작동하여 데이터를 수집하고 PostgreSQL에 저장합니다.
python crawler.py
```

**2. API 서버 실행 (Serve)**
```bash
# FastAPI 서버를 실행합니다.
uvicorn main:app --reload
```
- 서버 실행 후, 웹 브라우저에서 `http://127.0.0.1:8000/docs` 로 접속하면 자동 생성된 API 문서를 확인할 수 있습니다.

---

## 🔧 핵심 기능 및 문제 해결 경험

### 1. 동적 웹 페이지 크롤링 및 403 에러 해결

- **문제 상황**: 초기 분석 시 확인한 상품 랭킹 데이터 API(`getBestList.do`)에 직접 접근 시, 웹사이트의 봇 감지 시스템으로 인해 **403 Forbidden 에러**가 발생했습니다. 이는 단순히 HTTP 요청만으로는 데이터를 가져올 수 없음을 의미했습니다.

- **해결 과정**:
    1. `requests` 대신 **`Selenium`**을 사용하여 실제 사용자와 같이 웹 브라우저를 자동화하는 방식으로 접근했습니다.
    2. 단순히 URL을 이동하는 것을 넘어, **메인 페이지 접속 → '랭킹' 메뉴 클릭 → 페이지 이동**의 순차적인 사용자 행동을 모방하여 봇 감지를 우회하고 목표 페이지에 안정적으로 접근할 수 있었습니다.
    3. User-Agent 설정, 자동화 관련 플래그 비활성화 등 추가적인 옵션을 적용하여 크롤러의 안정성을 높였습니다.

- **배운 점**: 최신 웹사이트들은 다양한 방식으로 자동화된 접근을 차단하고 있음을 이해했습니다. 웹사이트의 구조와 정책을 파악하고, 실제 사용자 흐름을 시뮬레이션하는 것이 안정적인 데이터 수집의 핵심임을 배웠습니다.

### 2. CSS 속성을 활용한 동적 데이터 파싱

- **문제 상황**: 상품 평점 데이터가 HTML 텍스트가 아닌, CSS의 `style="width: 96%"` 와 같이 막대 그래프의 너비(width) 값으로 동적으로 표현되어 있었습니다. 일반적인 `.text` 속성으로는 데이터를 추출할 수 없었습니다.

- **해결 과정**:
    1. 해당 태그(`span.point`)의 `style` 속성값을 문자열로 추출했습니다.
    2. 정규표현식(RegEx)을 사용하여 `width` 값(예: '96')을 성공적으로 파싱했습니다.
    3. 파싱한 백분율 값을 **`round((percentage / 100) * 5, 1)`** 공식을 통해 5점 만점의 평점 점수(예: 4.8)로 변환하여 데이터를 정제했습니다.

- **배운 점**: 눈에 보이는 모든 데이터가 텍스트 형태로 존재하지 않는다는 것을 배웠습니다. 개발자 도구로 HTML 구조뿐만 아니라 CSS 스타일링까지 분석하여 숨겨진 데이터를 추출하는 역량을 기를 수 있었습니다.

### 3. FastAPI를 이용한 REST API 구축

- `main.py`에 엔드포인트를 구현하여 PostgreSQL에 저장된 상품 데이터를 외부에 JSON 형식으로 제공하는 API 서버를 구축했습니다.
- Pydantic 모델을 사용하여 API의 요청 및 응답 데이터 형식을 명확히 정의하고, 데이터 유효성을 검증하여 안정성을 높였습니다.
- FastAPI의 자동 API 문서 기능(`/docs`)을 활용하여 API 명세를 효율적으로 관리할 수 있습니다.

---

## 🚀 향후 발전 계획

- **스케줄링 자동화**: 매일 정해진 시간에 크롤러가 자동으로 실행되도록 `APScheduler`나 `Airflow`와 같은 스케줄러 도입.
- **클라우드 배포**: 전체 데이터 파이프라인을 AWS, GCP 등 클라우드 환경에 배포하여 안정적인 24시간 운영.
- **프론트엔드 시각화**: 수집된 데이터를 사용자가 보기 쉽게 차트나 테이블 형태로 보여주는 간단한 웹 페이지 개발 (React, Vue.js 등).
