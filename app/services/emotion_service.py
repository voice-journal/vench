from transformers import pipeline

# 1. Zero-Shot 분류 모델 로드
emotion_classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    device=-1 # CPU 사용
)

# 2. [Vench v2.0] 8가지 감정을 위한 정교한 영문 라벨 정의
# 모델은 영문 뉘앙스를 훨씬 잘 이해하므로, 비슷한 유의어를 여러 개 넣어 정확도를 높입니다.
CANDIDATE_LABELS = [
    "joy", "happiness",          # 기쁨
    "sadness", "grief",          # 슬픔
    "anger", "furious",          # 분노
    "anxiety", "worry",          # 불안
    "calmness", "neutral",       # 평온 (중립 포함)
    "tired", "exhausted",        # [New] 피로
    "proud", "accomplished",     # [New] 뿌듯
    "excited", "anticipating",   # [New] 설렘
]

# 3. 분석 결과를 UI용 한국어 라벨(8종)로 매핑
LABEL_MAP = {
    # 기존 5대 감정
    "joy": "기쁨",
    "happiness": "기쁨",
    "sadness": "슬픔",
    "grief": "슬픔",
    "anger": "분노",
    "furious": "분노",
    "anxiety": "불안",
    "worry": "불안",
    "calmness": "평온",
    "neutral": "평온",

    # [New] 신규 감정 3종
    "tired": "피로",
    "exhausted": "피로",
    "proud": "뿌듯",
    "accomplished": "뿌듯",
    "excited": "설렘",
    "anticipating": "설렘",
}

def analyze_emotion(text: str):
    """
    텍스트를 입력받아 8가지 세분화된 감정 중 하나로 분류합니다.
    """
    if not text:
        return {"label": "평온", "score": 0.0, "all_scores": []}

    # 4. 제로샷 분석 수행
    results = emotion_classifier(
        text,
        CANDIDATE_LABELS,
        multi_label=False,
        hypothesis_template="The emotion of this text is {}."
    )

    # 5. 점수가 가장 높은 감정 추출
    top_raw_label = results['labels'][0]
    top_score = results['scores'][0]

    # 6. 한국어 라벨로 변환
    final_label = LABEL_MAP.get(top_raw_label, "평온")

    # 7. 프론트엔드 차트용 점수 데이터 가공 (중복된 한글 라벨은 합산)
    score_dict = {
        "기쁨": 0.0, "슬픔": 0.0, "분노": 0.0, "불안": 0.0, "평온": 0.0,
        "피로": 0.0, "뿌듯": 0.0, "설렘": 0.0
    }

    for label, score in zip(results['labels'], results['scores']):
        korean_label = LABEL_MAP.get(label, "평온")
        if korean_label in score_dict:
            score_dict[korean_label] += score

    # 리스트 형태로 변환 (점수 높은 순 정렬)
    formatted_scores = [
        {"label": k, "score": v}
        for k, v in sorted(score_dict.items(), key=lambda item: item[1], reverse=True)
    ]

    return {
        "label": final_label,
        "score": top_score,
        "all_scores": formatted_scores
    }

if __name__ == "__main__":
    test_cases = [
        "와, 드디어 해냈다! 진짜 너무 기분 좋아.",   # 기쁨 or 뿌듯
        "오늘은 햄버거 먹고 빨리 집에 가서 자야겠다.", # 피로
        "내일 여행 간다! 빨리 짐 싸야지.",          # 설렘
        "아 진짜 아무것도 하기 싫다...",             # 피로
    ]

    print("🧪 감정 분석 테스트 시작 (8종 분류)...")
    for text in test_cases:
        res = analyze_emotion(text)
        print(f"\n📝 문장: {text}")
        print(f"🏆 결과: {res['label']} (Raw Top: {res['all_scores'][0]['score']:.2f})")
