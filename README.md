# 🛋️ Vench (Voice + Bench)
> **"잠시 쉬어가세요, 당신의 하루를 들어줄게요."**
>
> 목소리로 하루를 기록하면, AI가 다듬어주고 위로해주는 **로컬 기반 감성 일기장**

[![Stack](https://img.shields.io/badge/Tech-FastAPI%20%7C%20Streamlit%20%7C%20Docker-blue?style=flat-square)]()
[![AI](https://img.shields.io/badge/AI-Faster--Whisper%20%7C%20mDeBERTa%20%7C%20LG%20EXAONE-violet?style=flat-square)]()
[![Monitoring](https://img.shields.io/badge/Monitoring-Prometheus%20%7C%20Grafana%20%7C%20Loki-orange?style=flat-square)]()

## 🚀 프로젝트 개요
**Vench**는 현대인의 번아웃을 예방하고 마음을 돌보기 위한 **AI 멘탈 헬스케어 플랫폼**입니다.
사용자가 마이크에 대고 편안하게 이야기하면, AI가 감정을 분석하고 내용을 요약하여 일기로 써주며, 따뜻한 위로의 한마디를 건넵니다.

이 모든 과정은 **외부 API 호출 없이(Cost Zero)**, 사용자의 로컬 환경(Docker)에서 안전하게 수행되어 민감한 프라이버시를 완벽하게 보호합니다.

## ✨ 주요 기능 (Key Features)
* **🎤 고성능 음성 기록 (STT)**: `Faster-Whisper (Medium)` 모델을 탑재하여 한국어 음성을 빠르고 정확하게 텍스트로 변환합니다.
* **🧠 감정 정밀 분석 (8 Emotions)**: `mDeBERTa` 모델이 **8가지 핵심 감정**(기쁨, 슬픔, 분노, 불안, 평온, **피로, 뿌듯, 설렘**)을 분석하고 수치화합니다.
* **✍️ AI 일기 & 제목 생성**: **LG EXAONE 3.0 (7.8B)** LLM이 구어체 기록을 차분한 문어체 일기로 다듬고, 하루를 은유하는 **감성 제목**을 지어줍니다.
* **💌 맞춤형 위로 메시지**: 분석된 감정과 내용을 바탕으로 심리 상담사 페르소나의 AI가 따뜻한 위로를 건넵니다.
* **📊 주간 리포트 & 대시보드**: 내 감정의 흐름을 시각화된 차트로 확인하고, 관리자는 Grafana를 통해 서비스 지표를 모니터링할 수 있습니다.
* **⚡ 초고속 환경**: `uv` 패키지 매니저를 도입하여 빌드 및 배포 속도를 획기적으로 개선했습니다.

## 🛠️ 기술 스택 (Tech Stack)

| 구분 | 기술 (Technology) | 상세 내용 |
| :--- | :--- | :--- |
| **Backend** | **FastAPI** (Python 3.12) | 비동기 API 서버, 백그라운드 태스크(Celery 대체), SQLAlchemy ORM |
| **Frontend** | **Streamlit** | 반응형 대화형 UI, 실시간 데이터 시각화 (Altair), WebSocket Polling |
| **AI (STT)** | **Faster-Whisper** | `medium` 모델 (Int8 Quantized) - 고성능 한국어 음성 인식 |
| **AI (NLP)** | **Transformers** | `mDeBERTa-v3-base` - 제로샷 8종 감정 분류 |
| **AI (LLM)** | **Llama.cpp** | **LG EXAONE 3.0 7.8B Instruct (GGUF)** - 일기/제목/위로 생성 (Local LLM) |
| **Database** | **MySQL 8.0** | 사용자 정보, 일기 데이터, 감정 분석 결과 저장 |
| **DevOps** | **Docker Compose**, **uv** | 컨테이너 오케스트레이션 및 고속 패키지 관리 |
| **Monitoring** | **PLG Stack** | Prometheus(메트릭), Loki(로그), Grafana(대시보드), Promtail(로그 수집) |

## 🏗️ 시스템 아키텍처 (Architecture)
1.  **User**가 Streamlit UI를 통해 음성을 녹음 및 업로드합니다.
2.  **FastAPI** 서버가 요청을 받아 비동기 백그라운드 태스크로 처리를 위임하고 즉시 응답(`202 Accepted`)합니다.
3.  **Process Pipeline**:
    * **Preprocessing**: 오디오 볼륨 정규화 및 WAV 변환.
    * **STT**: 음성을 텍스트로 변환.
    * **Emotion Analysis**: 텍스트에서 8가지 감정 스코어 추출.
    * **Generation**: LLM이 일기 본문, 제목, 위로 메시지 생성.
4.  모든 결과는 **MySQL**에 저장되며, UI는 Polling을 통해 실시간으로 진행 상황을 표시합니다.
5.  **Monitoring**: 서버 상태와 비즈니스 지표는 Prometheus/Loki로 수집되어 Grafana 대시보드에 표출됩니다.

## 🏃 시작하기 (Quick Start)

### 권장 사양
* **OS**: Windows, macOS (M-series 권장), Linux
* **RAM**: **16GB 이상 권장** (LLM 모델 구동을 위해 최소 8GB 이상의 여유 메모리가 필요합니다)
* **Disk**: 약 10GB 여유 공간 (Docker 이미지 및 AI 모델 가중치 파일)

### 설치 및 실행

**1. 저장소 복제**
```bash
git clone [https://github.com/voice-journal/vench.git](https://github.com/voice-journal/vench.git)
cd vench
```
**2. 환경 변수 설정 .env.template 파일을 복사하여 .env 파일을 생성합니다.**
```bash
cp .env.template .env
# 필요시 .env 파일 내부의 비밀번호 등을 수정하세요.
```
**3. 서비스 실행 (Docker Compose) 최초 실행 시 LG EXAONE 3.0 모델(약 5GB) 및 Whisper 모델을 다운로드하므로 시간이 소요될 수 있습니다.**
```bash
docker-compose up -d --build
```
**4. 접속 정보**
```bash
Frontend (서비스): http://localhost:8501

Backend Docs (Swagger): http://localhost:8000/docs

Grafana (모니터링): http://localhost:3000 (ID: admin / PW: admin 초기 설정)
```
**🔐 초기 계정 (Initial Accounts)**
```
앱 실행 시 자동으로 생성되는 테스트 계정입니다. [app/core/init_data.py]
관리자:admin@vench.com/12341234/전체 기능 + 관리자 대시보드 접근
테스트 유저:user@vench.com/12341234/일반 사용자 기능
```
**📂 프로젝트 구조 (Directory Structure)**
```bash
vench/
├── app/
│   ├── api/             # API 라우터 설정
│   ├── core/            # 설정, DB, 보안, 로깅, 예외 처리
│   ├── domains/         # 도메인별 로직 (Auth, Diary, Feedback, Report)
│   ├── services/        # AI 및 비즈니스 로직 (STT, Emotion, LLM, Monitoring)
│   ├── views/           # Streamlit Frontend 화면 구성
│   └── main.py          # FastAPI 엔트리포인트
├── data/
│   ├── models/          # AI 모델 캐시 (HuggingFace/Llama.cpp)
│   └── mysql/           # DB 데이터 영구 저장소
├── grafana/             # Grafana 프로비저닝 설정
├── Dockerfile           # Backend/Frontend 통합 이미지 빌드 설정
├── docker-compose.yml   # 전체 서비스 오케스트레이션
└── requirements.txt     # Python 의존성 목록
```
**⚠️ 초기화 방법 (데이터 삭제)**
개발 중 데이터를 모두 초기화하고 싶다면 다음 명령어를 사용하세요.
```bash
# 1. 컨테이너 종료 및 DB 볼륨(데이터) 삭제
docker-compose down -v

# 2. (선택) 로컬에 생성된 오디오/DB 데이터 폴더 정리
rm -rf data/mysql/* data/audio/*

# 🚨 주의: data/models 폴더는 삭제하지 마세요! (모델을 다시 받아야 합니다)
```
