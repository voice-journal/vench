from transformers import pipeline

# 1. 모델 로드 (전역 변수로 한 번만 로드)
# 한국어 감정 분석에 탁월한 'roberta' 모델을 사용합니다.
# 처음 실행할 때 모델을 다운로드하느라 시간이 좀 걸립니다.
emotion_pipeline = pipeline(
    "text-classification",
    model="matthewburke/korean_sentiment",
    top_k=None
)

def analyze_emotion(text: str):
    """
    텍스트를 입력받아 {라벨, 점수, 전체결과}를 반환합니다.
    """
    if not text:
        return {"label": "neutral", "score": 0.0}

    # 2. 분석 수행
    results = emotion_pipeline(text)
    # results 예시: [[{'label': 'LABEL_0', 'score': 0.1}, {'label': 'LABEL_1', 'score': 0.9}]]

    # 3. 가장 점수가 높은 감정 찾기
    top_result = max(results[0], key=lambda x: x['score'])

    # 4. 라벨 이름 보기 좋게 변환 (모델마다 다름)
    # 이 모델은 LABEL_0: 부정(negative), LABEL_1: 긍정(positive) 입니다.
    label_map = {"LABEL_0": "negative", "LABEL_1": "positive"}
    mapped_label = label_map.get(top_result['label'], top_result['label'])

    return {
        "label": mapped_label,
        "score": top_result['score'],
        "all_scores": results[0]
    }

# --- 로컬 테스트용 코드 ---
# 이 파일을 직접 실행(python -m ...)할 때만 작동합니다.
if __name__ == "__main__":
    print("⏳ 모델 로딩 중... (잠시만 기다려주세요)")
    test_text = "와, 드디어 서버 고쳤다! 기분 너무 좋아."
    result = analyze_emotion(test_text)
    print(f"✅ 테스트 문장: {test_text}")
    print(f"📊 분석 결과: {result}")
