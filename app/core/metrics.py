from prometheus_client import Gauge

# 1. 총 사용자 수 (Total Users)
# 예: vench_total_users 120
TOTAL_USERS = Gauge("vench_total_users", "Total number of registered users")

# 2. 누적 일기 수 (Total Diaries)
# 예: vench_total_diaries 450
TOTAL_DIARIES = Gauge("vench_total_diaries", "Total number of diaries created")

# 3. 감정별 일기 수 (Emotion Distribution)
# 예: vench_emotion_count{label="기쁨"} 30
EMOTION_COUNT = Gauge("vench_emotion_count", "Number of diaries by emotion", ["label"])
