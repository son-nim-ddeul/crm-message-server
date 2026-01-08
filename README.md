# crm-message-generator

## Docker 실행 방법

이 프로젝트는 `uv`를 사용하여 최적화된 Docker 환경을 제공합니다.

### 1. Docker Compose로 실행 (권장)

이 프로젝트는 `profiles`를 사용하여 각 서버를 독립적으로 실행합니다. 동시에 실행되지 않으므로 원하는 프로파일을 명시해야 합니다.

#### Agent 서비스 실행 (8080 포트)
```bash
docker-compose --profile agent up --build
```
- `http://localhost:8080`

#### API 서비스 실행 (8000 포트)
```bash
docker-compose --profile api up --build
```
- `http://localhost:8000`

- **Agent**: [http://localhost:8080](http://localhost:8080)
- **API**: [http://localhost:8000](http://localhost:8000)
