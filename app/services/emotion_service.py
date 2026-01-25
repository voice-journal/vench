from transformers import pipeline

# 1. Zero-Shot 분류 모델 로드
# MoritzLaurer/mDeBERTa-v3-base-mnli-xnli: 다국어(한국어 포함) 지원 및 고성능 Zero-shot 모델
emotion_classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    device=-1 # CPU 사용 (GPU 있으면 0)
)

# 2. 분석할 5가지 감정 키워드
TARGET_LABELS = ["기쁨", "슬픔", "분노", "불안", "평온"]

def analyze_emotion(text: str):
    """
    텍스트를 입력받아 5가지 감정 중 가장 높은 것과 전체 점수를 반환합니다.
    """
    if not text:
        return {"label": "평온", "score": 0.0, "all_scores": []}

    # 3. 제로샷 분석 수행
    # hypothesis_template는 한국어 문맥에 맞게 설정하면 성능이 더 좋아집니다.
    results = emotion_classifier(
        text,
        TARGET_LABELS,
        multi_label=False,
        hypothesis_template="이 문장의 감정은 {}입니다."
    )

    # 4. 가장 높은 점수의 감정 추출
    top_label = results['labels'][0]
    top_score = results['scores'][0]

    # 5. 프론트엔드용 포맷 변환
    formatted_scores = [
        {"label": label, "score": score}
        for label, score in zip(results['labels'], results['scores'])
    ]

    return {
        "label": top_label,       # 1등 감정
        "score": top_score,       # 1등 점수
        "all_scores": formatted_scores # 전체 순위
    }

# --- 로컬 테스트용 코드 ---
if __name__ == "__main__":
    print("⏳ 모델 로딩 중... (약 1GB 다운로드, 조금 걸립니다)")
    test_text = "와, 드디어 해냈다! 진짜 너무 기분 좋아."
    result = analyze_emotion(test_text)

    print(f"✅ 테스트 문장: {test_text}")
    print(f"🏆 대표 감정: {result['label']} ({result['score']*100:.1f}%)")
    print("📊 전체 분포:", result['all_scores'])
