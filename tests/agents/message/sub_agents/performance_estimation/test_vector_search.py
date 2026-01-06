import json
from unittest.mock import patch

# src.config 모킹 (테스트 환경에서 .env 파일 접근 오류 방지)
with patch("src.config.settings") as mock_settings:
    mock_settings.rds_db_path = ":memory:"
    mock_settings.vector_db_path = ":memory:"
    from agents.message.sub_agents.performance_estimation.utils import find_previous_messages
    from database.vector_manager import VectorManager
    from database.session import load_vec_extension

# API On/Off 스위치 (True: 실제 DB 사용, False: Mock 사용)
USE_REAL_VECTOR_DB = False

# 32개의 Stub 데이터 정의 (4개 감정 x 4개 계절 x 2개 예시)
STUB_MESSAGES = [
    # 1. 열망 자극형 (Aspiration)
    # 봄
    {"content": "새로운 시작의 계절, 당신의 꿈에 날개를 달아줄 완벽한 기회를 놓치지 마세요.", "metadata": {"brand_tone": "Aspirational", "message_purpose": "Sales", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-03-15 00:00:00", "product_info": "Growth Course", "holidays": ["2024-03-01 삼일절"], "season": "2024-03-15 봄"}},
    {"content": "봄의 활기처럼 당신의 잠재력을 깨워보세요. 최고의 당신을 향한 첫걸음을 응원합니다.", "metadata": {"brand_tone": "Aspirational", "message_purpose": "Engagement", "key_marketing_achievements": "CVR", "message_sending_datetime": "2024-04-10 00:00:00", "product_info": "Mentoring", "holidays": ["2024-04-10 국회의원 선거"], "season": "2024-04-10 봄"}},
    # 여름
    {"content": "뜨거운 태양 아래 더욱 빛나는 당신, 목표를 향한 열정으로 이번 여름을 평정하세요.", "metadata": {"brand_tone": "Aspirational", "message_purpose": "Sales", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-07-10 00:00:00", "product_info": "Summer Camp", "holidays": [], "season": "2024-07-10 여름"}},
    {"content": "누구보다 부러워할 당신만의 당당함, 여름의 주인공이 될 준비가 되셨나요?", "metadata": {"brand_tone": "Aspirational", "message_purpose": "Sales", "key_marketing_achievements": "ROAS", "message_sending_datetime": "2024-08-05 00:00:00", "product_info": "Premium Fashion", "holidays": ["2024-08-15 광복절"], "season": "2024-08-05 여름"}},
    # 가을
    {"content": "수확의 계절, 그동안의 노력이 결실을 맺을 시간입니다. 더 높은 성취를 향해 나아가세요.", "metadata": {"brand_tone": "Aspirational", "message_purpose": "Engagement", "key_marketing_achievements": "CVR", "message_sending_datetime": "2024-09-20 00:00:00", "product_info": "Wealth Management", "holidays": ["2024-09-16 추석", "2024-09-17 추석", "2024-09-18 추석"], "season": "2024-09-20 가을"}},
    {"content": "깊어가는 가을만큼 깊어지는 당신의 가치, 프리미엄의 품격으로 당신을 증명하세요.", "metadata": {"brand_tone": "Aspirational", "message_purpose": "Sales", "key_marketing_achievements": "ROAS", "message_sending_datetime": "2024-10-15 00:00:00", "product_info": "Luxury Watch", "holidays": ["2024-10-03 개천절", "2024-10-09 한글날"], "season": "2024-10-15 가을"}},
    # 겨울
    {"content": "추운 겨울을 녹이는 뜨거운 야망, 당신의 도전은 계절을 가리지 않습니다.", "metadata": {"brand_tone": "Aspirational", "message_purpose": "Engagement", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-12-05 00:00:00", "product_info": "Challenge 2025", "holidays": ["2024-12-25 기독탄신일"], "season": "2024-12-05 겨울"}},
    {"content": "새해를 앞둔 지금, 한계를 넘어선 도약으로 누구보다 먼저 성공을 선점하세요.", "metadata": {"brand_tone": "Aspirational", "message_purpose": "Sales", "key_marketing_achievements": "CVR", "message_sending_datetime": "2025-01-05 00:00:00", "product_info": "Career Coaching", "holidays": ["2025-01-01 신정"], "season": "2025-01-05 겨울"}},

    # 2. 공감 지원형 (Empathy)
    # 봄
    {"content": "나른한 봄날, 당신의 마음에도 따뜻한 볕이 들길 바라요. 잠시 쉬어가도 괜찮습니다.", "metadata": {"brand_tone": "Empathetic", "message_purpose": "Retention", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-03-20 00:00:00", "product_info": "Healing App", "holidays": ["2024-03-01 삼일절"], "season": "2024-03-20 봄"}},
    {"content": "새로운 환경이 낯설고 힘들지 않나요? 우리가 당신의 든든한 버팀목이 되어드릴게요.", "metadata": {"brand_tone": "Empathetic", "message_purpose": "Retention", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-04-25 00:00:00", "product_info": "Counseling", "holidays": ["2024-04-10 국회의원 선거"], "season": "2024-04-25 봄"}},
    # 여름
    {"content": "지치기 쉬운 무더위 속에서도 묵묵히 자리를 지키는 당신, 정말 대단해요. 시원한 위로를 전합니다.", "metadata": {"brand_tone": "Empathetic", "message_purpose": "Retention", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-07-20 00:00:00", "product_info": "Cooling Goods", "holidays": [], "season": "2024-07-20 여름"}},
    {"content": "장마철 눅눅한 기분까지 뽀송하게 말려줄 따뜻한 한마디, 당신은 충분히 잘하고 있어요.", "metadata": {"brand_tone": "Empathetic", "message_purpose": "Retention", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-08-15 00:00:00", "product_info": "Dehumidifier", "holidays": ["2024-08-15 광복절"], "season": "2024-08-15 여름"}},
    # 가을
    {"content": "쓸쓸해지기 쉬운 가을바람에 마음이 흔들린다면, 우리가 당신을 꼭 안아드릴게요.", "metadata": {"brand_tone": "Empathetic", "message_purpose": "Retention", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-09-30 00:00:00", "product_info": "Cozy Blanket", "holidays": ["2024-09-16 추석", "2024-09-17 추석", "2024-09-18 추석"], "season": "2024-09-30 가을"}},
    {"content": "바쁜 일상 속 잊고 지낸 당신의 소중한 시간, 잠시 멈춰 서서 당신을 돌봐주세요.", "metadata": {"brand_tone": "Empathetic", "message_purpose": "Retention", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-10-20 00:00:00", "product_info": "Meditation Kit", "holidays": ["2024-10-03 개천절", "2024-10-09 한글날"], "season": "2024-10-20 가을"}},
    # 겨울
    {"content": "시린 겨울바람도 녹여줄 포근한 공감, 당신의 추운 하루 끝에 우리가 함께하겠습니다.", "metadata": {"brand_tone": "Empathetic", "message_purpose": "Retention", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-12-15 00:00:00", "product_info": "Winter Tea", "holidays": ["2024-12-25 기독탄신일"], "season": "2024-12-15 겨울"}},
    {"content": "다사다난했던 올 한 해, 정말 수고 많으셨습니다. 당신의 모든 순간을 진심으로 이해합니다.", "metadata": {"brand_tone": "Empathetic", "message_purpose": "Retention", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-12-31 00:00:00", "product_info": "Year-end Diary", "holidays": ["2024-12-25 기독탄신일", "2025-01-01 신정"], "season": "2024-12-31 겨울"}},

    # 3. 즐거움 엔터테이너형 (Joy)
    # 봄
    {"content": "꽃바람 타고 찾아온 짜릿한 소식! 지금 바로 봄맞이 축제의 주인공이 되어보세요!", "metadata": {"brand_tone": "Playful", "message_purpose": "Promotion", "key_marketing_achievements": "CPC", "message_sending_datetime": "2024-03-10 00:00:00", "product_info": "Festival Ticket", "holidays": ["2024-03-01 삼일절"], "season": "2024-03-10 봄"}},
    {"content": "상큼발랄 봄꽃처럼 톡톡 튀는 즐거움이 가득! 지루할 틈 없는 이벤트가 시작됩니다!", "metadata": {"brand_tone": "Playful", "message_purpose": "Promotion", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-04-05 00:00:00", "product_info": "Mystery Box", "holidays": ["2024-04-10 국회의원 선거"], "season": "2024-04-05 봄"}},
    # 여름
    {"content": "답답한 일상을 날려버릴 시원한 파티! 상상만 해도 즐거운 여름 휴가를 지금 떠나세요!", "metadata": {"brand_tone": "Playful", "message_purpose": "Promotion", "key_marketing_achievements": "CPC", "message_sending_datetime": "2024-06-25 00:00:00", "product_info": "Pool Party", "holidays": [], "season": "2024-06-25 여름"}},
    {"content": "무더위를 한 방에 날려줄 역대급 재미! 텐션 업! 신나는 여름 밤을 즐겨봐요!", "metadata": {"brand_tone": "Playful", "message_purpose": "Promotion", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-07-30 00:00:00", "product_info": "Night Market", "holidays": [], "season": "2024-07-30 여름"}},
    # 가을
    {"content": "단풍만큼 다채로운 즐거움이 팡팡! 가을 소풍 가듯 가벼운 마음으로 축제를 즐기세요!", "metadata": {"brand_tone": "Playful", "message_purpose": "Promotion", "key_marketing_achievements": "CPC", "message_sending_datetime": "2024-10-05 00:00:00", "product_info": "Theme Park", "holidays": ["2024-10-03 개천절", "2024-10-09 한글날"], "season": "2024-10-05 가을"}},
    {"content": "가을 밤의 낭만과 재미를 동시에! 웃음꽃 피어나는 특별한 모먼트를 놓치지 마세요!", "metadata": {"brand_tone": "Playful", "message_purpose": "Promotion", "key_marketing_achievements": "CTR", "message_sending_datetime": "2024-11-10 00:00:00", "product_info": "Movie Night", "holidays": [], "season": "2024-11-10 가을"}},
    # 겨울
    {"content": "눈꽃처럼 쏟아지는 화려한 혜택! 크리스마스의 설렘을 담아 즐거움을 선물합니다!", "metadata": {"brand_tone": "Playful", "message_purpose": "Promotion", "key_marketing_achievements": "CPC", "message_sending_datetime": "2024-12-20 00:00:00", "product_info": "Gift Card", "holidays": ["2024-12-25 기독탄신일"], "season": "2024-12-20 겨울"}},
    {"content": "춥다고 웅크려 있지 마세요! 겨울에도 멈추지 않는 짜릿한 액티비티가 기다립니다!", "metadata": {"brand_tone": "Playful", "message_purpose": "Promotion", "key_marketing_achievements": "CPM", "message_sending_datetime": "2025-01-20 00:00:00", "product_info": "Ski Resort", "holidays": ["2025-01-01 신정", "2025-01-28 설날", "2025-01-29 설날", "2025-01-30 설날"], "season": "2025-01-20 겨울"}},

    # 4. 이성적 조언자형 (Rational Advisor)
    # 봄
    {"content": "계획적인 시작이 성공을 결정합니다. 봄의 루틴을 분석하여 최적의 효율을 찾아보세요.", "metadata": {"brand_tone": "Rational", "message_purpose": "Advice", "key_marketing_achievements": "ROAS", "message_sending_datetime": "2024-03-05 00:00:00", "product_info": "Planner", "holidays": ["2024-03-01 삼일절"], "season": "2024-03-05 봄"}},
    {"content": "변화하는 시장 트렌드에 맞춰 당신의 자산을 점검할 때입니다. 전문가의 가이드를 확인하세요.", "metadata": {"brand_tone": "Rational", "message_purpose": "Advice", "key_marketing_achievements": "CPA", "message_sending_datetime": "2024-04-15 00:00:00", "product_info": "Market Report", "holidays": ["2024-04-10 국회의원 선거"], "season": "2024-04-15 봄"}},
    # 여름
    {"content": "휴가철 소비 패턴을 분석하면 지출은 줄이고 가치는 높일 수 있습니다. 스마트한 여름 설계를 시작하세요.", "metadata": {"brand_tone": "Rational", "message_purpose": "Advice", "key_marketing_achievements": "ROAS", "message_sending_datetime": "2024-06-15 00:00:00", "product_info": "Expense Tracker", "holidays": ["2024-06-06 현충일"], "season": "2024-06-15 여름"}},
    {"content": "여름철 건강 관리, 데이터로 증명된 체계적인 솔루션으로 확실하게 챙기세요.", "metadata": {"brand_tone": "Rational", "message_purpose": "Advice", "key_marketing_achievements": "CPA", "message_sending_datetime": "2024-07-25 00:00:00", "product_info": "Health Analysis", "holidays": [], "season": "2024-07-25 여름"}},
    # 가을
    {"content": "상반기 성과를 되돌아보고 하반기 전략을 정비할 시간입니다. 논리적인 분석이 답을 줍니다.", "metadata": {"brand_tone": "Rational", "message_purpose": "Advice", "key_marketing_achievements": "ROAS", "message_sending_datetime": "2024-09-10 00:00:00", "product_info": "Business Insight", "holidays": ["2024-09-16 추석", "2024-09-17 추석", "2024-09-18 추석"], "season": "2024-09-10 가을"}},
    {"content": "가을의 합리적인 선택이 겨울의 여유를 만듭니다. 지금 바로 검증된 정보를 토대로 결단하세요.", "metadata": {"brand_tone": "Rational", "message_purpose": "Advice", "key_marketing_achievements": "CPA", "message_sending_datetime": "2024-10-25 00:00:00", "product_info": "Investment Guide", "holidays": ["2024-10-03 개천절", "2024-10-09 한글날"], "season": "2024-10-25 가을"}},
    # 겨울
    {"content": "연말 정산부터 내년 예산까지, 수치로 확인하는 명확한 비전이 당신의 자산을 지킵니다.", "metadata": {"brand_tone": "Rational", "message_purpose": "Advice", "key_marketing_achievements": "ROAS", "message_sending_datetime": "2024-12-10 00:00:00", "product_info": "Accounting Tool", "holidays": ["2024-12-25 기독탄신일"], "season": "2024-12-10 겨울"}},
    {"content": "기온은 떨어져도 효율은 올라가야 합니다. 겨울철 최적의 퍼포먼스를 위한 분석 리포트를 확인하세요.", "metadata": {"brand_tone": "Rational", "message_purpose": "Advice", "key_marketing_achievements": "CPA", "message_sending_datetime": "2025-02-05 00:00:00", "product_info": "Efficiency Report", "holidays": ["2025-03-01 삼일절"], "season": "2025-02-05 겨울"}},
]

def test_find_previous_messages():
    # pipeline.py의 current_message_info 포맷에 맞춘 테스트 쿼리
    test_query = {
        "content": "지친 일상에 활력을 불어넣어 줄 특별한 휴가 계획, 지금 세워보세요!",
        "metadata": {
            "brand_tone": "Empathetic",
            "message_purpose": "Retention",
            "key_marketing_achievements": "CTR",
            "message_sending_datetime": "2024-07-01 00:00:00",
            "product_info": "Summer Vacation Package",
            "holidays": [],
            "season": "2024-07-01 여름"
        }
    }
    top_k = 3

    if not USE_REAL_VECTOR_DB:
        # 1. Mock 모드 (API Off)
        print("\n--- Running Mock Mode (API Off) ---")
        with patch("agents.message.sub_agents.performance_estimation.utils.VectorManager") as MockVM:
            mock_instance = MockVM.return_value
            # search_similar가 STUB_MESSAGES 중 일부를 반환하도록 설정
            # Empathy(공감 지원형) 중 하나와 Joy(즐거움형) 중 하나를 반환하도록 예시 설정
            mock_instance.search_similar.return_value = [
                {"key": "stub", "content": json.dumps(STUB_MESSAGES[10], ensure_ascii=False), "metadata": STUB_MESSAGES[10]["metadata"], "distance": 0.15},
                {"key": "stub", "content": json.dumps(STUB_MESSAGES[18], ensure_ascii=False), "metadata": STUB_MESSAGES[18]["metadata"], "distance": 0.25}
            ]
            
            results = find_previous_messages(test_query, top_k=top_k)
            
            # 응답 결과 정확성 검증 (Assertion)
            assert len(results) == 2
            # STUB_MESSAGES[10]은 "여름" 공감 지원형, [18]은 "여름" 즐거움형
            assert "위로" in results[0]["content"] or "파티" in results[0]["content"]
            assert results[0]["metadata"]["key_marketing_achievements"] in ["CTR", "CPC"]
            print("[Mock Mode] Assertions passed.")
            
    else:
        # 2. 실제 DB 모드 (API On)
        print("\n--- Running Real DB Mode (API On) ---")
        from sqlalchemy import create_engine, event
        
        # 인메모리 SQLite DB 생성 (sqlite-vec 지원 필요)
        engine = create_engine("sqlite:///:memory:")
        event.listen(engine, "connect", load_vec_extension)
        
        # VectorManager 초기화 (인메모리 엔진 주입)
        vm = VectorManager(engine=engine)
        
        # Stub 데이터 삽입
        print(f"[Real DB Mode] Inserting {len(STUB_MESSAGES)} stub items...")
        for msg in STUB_MESSAGES:
            # find_previous_messages에서 json.dumps(message_info)로 검색하므로, 
            # 검색 대상인 content도 동일한 JSON 포맷으로 저장해야 함
            vm.add_item(key="stub", content=json.dumps(msg, ensure_ascii=False), metadata=msg["metadata"])
            
        # find_previous_messages 내의 VectorManager를 인메모리 인스턴스로 교체
        with patch("agents.message.sub_agents.performance_estimation.utils.VectorManager", return_value=vm):
            results = find_previous_messages(test_query, top_k=top_k)
            
        # 결과 로깅 (Assertion 대신 Print문으로 사용자가 확인)
        print(f"[Real DB Mode] Query Content: {test_query['content']}")
        print(f"[Real DB Mode] Found {len(results)} results:")
        for i, res in enumerate(results):
            print(f"  {i+1}. Distance: {res.get('distance', 'N/A')}")
            # res['content']는 JSON 문자열이므로 파싱해서 메세지만 출력하거나 전체 출력
            try:
                content_obj = json.loads(res['content'])
                print(f"     Message: {content_obj.get('content')}")
            except:
                print(f"     Content: {res['content']}")
            print(f"     Metadata: {res['metadata']}")
        print("[Real DB Mode] Please verify the relevance of the results manually.")

if __name__ == "__main__":
    # 스위치를 바꿔가며 직접 실행해볼 수 있도록 구성
    print("Running tests manually...")
    
    print("\n>>> Testing with USE_REAL_VECTOR_DB = False")
    USE_REAL_VECTOR_DB = False
    test_find_previous_messages()
    
    try:
        print("\n>>> Testing with USE_REAL_VECTOR_DB = True")
        USE_REAL_VECTOR_DB = True
        test_find_previous_messages()
    except Exception as e:
        print(f"\n[Error] Real DB Mode failed (Check if sqlite-vec is installed): {e}")
