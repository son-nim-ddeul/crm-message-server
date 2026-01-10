# TODO LIST
---
### 1. agents/config.py
[] 각 동작별 모델 수정 ex. writer_model = claude 사용 등
- 후순위 작업사항 (비용 고려)
---
### 2. agents/persona - 파일 업로드 기능
[] 사용자의 파일 업로드 (ex. 트렌드 리서치 리포트)
- mime_type 사전 정의 필요 (ex. pdf only)
- upload size 사전 정의 필요 (ex. 5mb 이하)
- API 구성 설계 필요
    - ex. 파일 업로드 API 와 페르소나 생성 API를 별개로
    - ex. 페르소나 생성 API에서 파일업로드를 받도록
    - 파일관리 필요
---
### 3. agents/persona - agents 프로세스 설계 및 구현
[] 페르소나 에이전트 root_agent 및 sub_agents 프로세스 설계
- agents/message에서 사용중인 페르소나 포맷에 맞는 페르소나 생성
    - ex. 페르소나 생성 갯수 고려
    - ex. 페르소나 다양성을 위한 워크플로우 구성 고려
- 참고 : https://github.com/google/adk-samples
---
### 4. agents/persona - 페르소나 DB 및 API 생성
[] 페르소나 에이전트에서 생성한 페르소나 관리
- 에이전트가 생성한 페르소나를 DB에 저장 및 테이블 설계
    - ex. persona_example.json 삭제
    - ex. 사용자별 페르소나 그룹 관리 등
    - ex. 페르소나 Image 어떤식으로 어디에서 관리할지
- 하나의 서버에서 페르소나 관리를 위한 API 추가
---
### 5. agents/message/agent.py - 임시데이터 관리
[] agent 직접 테스트를 위해 작성한 임시데이터 관리
- ex. state내 "dev_test" 값이 True인 경우에만 임시데이터 설정 등
---
### 6. agents/message/performance_estimation - RAG 데이터 활용 고도화
[] 현재 사용중인 RAG 비즈니스 로직 개선
- 정확한 마케팅 성과 예측을 위한 RAG 데이터 사용 방법 개선
- ex. 마케팅 메시지 tone, category (신규 회원 유입, 구매 유도 등)
- ex. 현재 사용중인 metadata를 활용한 비즈니스 로직, 알고리즘
---
### 7. global_memory_cache 동작 개선
[] 글로벌 캐시 활용 고도화
- 현재는 인메모리 캐시구조로 메모리 관리에 대한 코드가 부족
- ex. 사용 후 메모리 clear, 메모리 관리 API 등으로 개선이 진행될 수 있음
---
### 8. yield event에 따른 response 정리
[] 프론트에서 노출 및 사용할 response 필드 재정의
- 현재는 필요할법한 내용들을 임의로 응답 반환
- 실제 필요한 값들만 응답 재정의하여 경량화된 응답 반환
- contents 내부 반환되는 str json을 활용 가능하도록 포맷팅
---
### 9. 토큰 사용량 관리 및 최적화
[] 토큰 사용량 관리 비즈니스 로직 개선
- 토큰 사용은 현재 Events 테이블에 컬럼으로 관리됨
- 해당 토큰에 대한 관리, 필터링, 통계 로직 부재
- 관리 및 최적화를 통해 개선 시, 정확한 토큰 수치를 제시 가능함
- ex. n개의 토큰 사용에서 A 기능을 통해 00% 비용 최적화 하였다.
---
### 10. Agent DB관련 API
[] sql_lite Database 확인 및 관리 API 추가
- 데이터를 확인 하거나 관리 편의용 API 추가
- 프론트와 adk 서버간 동일 Database 데이터 활용 가능
---
### 11. cms 페이지 추가
[] 현재 agents 정보 조회, 사용량 조회 등 기능 추가
- 제출 및 프레젠테이션 시, 시각화 정보 제공 가능