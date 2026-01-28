# 🛋️ Vench (Voice + Bench)
> **"번아웃 온 당신, 30초만 털어놓으세요. 기록과 분석은 AI가 합니다."**

## 🚀 프로젝트 개요
Vench는 직장인의 번아웃을 예방하기 위해 목소리로 감정을 기록하고 AI가 이를 분석하여 위로와 인사이트를 제공하는 **멘탈 헬스케어 플랫폼**입니다.

## 💡 핵심 전략: "Local All-in"
* **고성능 로컬 서버:** MacBook M4 Pro를 메인 서버로 활용하여 지연 시간(Latency) 최소화.
* **비용 제로:** 외부 API 없이 로컬 AI 모델(Whisper, DeBERTa)만으로 구동.
* **철저한 보안:** 모든 음성 데이터는 로컬 DB(MySQL)에 안전하게 보관.

## 🛠️ 기술 스택 (Tech Stack)
| 구분 | 기술 | 역할 |
| :--- | :--- | :--- |
| **Backend** | FastAPI (v3.12) | 비동기 API 서버 및 백그라운드 태스크 관리 |
| **Frontend** | Streamlit | 대화형 UI 및 감정 분석 대시보드 |
| **AI (STT)** | faster-whisper (Int8) | 고속 음성-텍스트 변환 |
| **AI (NLP)** | mDeBERTa-v3 | 제로샷 감정 분류 (기쁨/슬픔/분노/불안/평온) |
| **Database** | MySQL 8.0 | 사용자 정보 및 일기/피드백 데이터 저장 |
| **Monitoring** | PLG Stack | Prometheus, Loki, Grafana를 이용한 통합 관제 |

## 🏗️ 시스템 아키텍처


## 🏃 시작하기 (Quick Start)
```bash
# 1. 저장소 복제 및 이동
git clone [https://github.com/voice-journal/vench.git](https://github.com/voice-journal/vench.git)
cd vench

# 2. 로컬 실행 (Docker Compose)
docker-compose up -d --build
