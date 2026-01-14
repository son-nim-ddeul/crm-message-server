# crm-message-generator

CRM 메시지 생성기를 위한 AI 에이전트 시스템입니다.

## 사전 요구사항

- Python 3.13 이상
- [uv](https://github.com/astral-sh/uv) 패키지 매니저
- Docker 및 Docker Compose (Docker 실행 시)
- Google API Key (GOOGLE_API_KEY)

## 시작하기

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다:

```bash
cp .env_example .env
```

`.env` 파일에 다음 내용을 추가하세요:

```env
GOOGLE_GEN_AI_VERTEXAI=false
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. 로컬 실행 방법

#### 의존성 설치

```bash
# uv를 사용하여 의존성 설치
uv sync
```

#### ADK Web으로 실행 (권장)

ADK의 웹 인터페이스를 사용하여 에이전트를 실행할 수 있습니다:

```bash
# ADK web 서버 실행
uv run adk web
```

또는 App을 직접 지정:

```bash
# 특정 App 지정하여 실행
uv run adk web --app agents.message.agent:app
```

서버가 실행되면 터미널에 표시된 주소(일반적으로 `http://localhost:8000`)로 웹 브라우저에서 접근할 수 있습니다.

#### API 서버 실행

```bash
# 가상 환경 활성화 후 실행
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

또는:

```bash
# main.py를 직접 실행
uv run python main.py
```

서버가 실행되면 다음 주소에서 접근할 수 있습니다:
- **API 서버**: [http://localhost:8000](http://localhost:8000)
- **API 문서**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Docker 실행 방법

이 프로젝트는 `uv`를 사용하여 최적화된 Docker 환경을 제공합니다.

#### Docker Compose로 실행 (권장)

이 프로젝트는 `profiles`를 사용하여 각 서버를 독립적으로 실행합니다. 동시에 실행되지 않으므로 원하는 프로파일을 명시해야 합니다.

**Agent 서비스 실행 (8080 포트)**
```bash
docker-compose --profile agent up --build
```
- `http://localhost:8080`

**API 서비스 실행 (8000 포트)**
```bash
docker-compose --profile api up --build
```
- `http://localhost:8000`
- **API 문서**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. 테스트 실행

```bash
# pytest를 사용하여 테스트 실행
uv run pytest
```

## 주요 기능

- **메시지 생성**: AI 기반 CRM 메시지 생성
- **벡터 검색**: SQLite + sqlite-vec를 활용한 유사도 기반 검색
- **페르소나 관리**: 사용자 페르소나 기반 메시지 커스터마이징
- **성능 추정**: 메시지 성능 예측 및 평가

## 프로젝트 구조

```
crm-message-generator/
├── agents/              # AI 에이전트 로직
├── database/            # 데이터베이스 모듈 (RDS + Vector DB)
├── src/                 # FastAPI 웹 서비스
├── tests/               # 테스트 코드
└── pyproject.toml       # 프로젝트 설정 및 의존성
```
