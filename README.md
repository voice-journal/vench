# 🛋️ Vench (Voice + Bench)
> **"잠시 쉬어가세요, 당신의 하루를 들어줄게요."**
>
> 목소리로 하루를 기록하면, AI가 다듬어주고 위로해주는 **로컬 기반 감성 일기장**

## 🚀 프로젝트 개요
**Vench**는 현대인의 번아웃을 예방하고 마음을 돌보기 위한 **AI 멘탈 헬스케어 플랫폼**입니다.
사용자가 마이크에 대고 편안하게 이야기하면, AI가 감정을 분석하고, 내용을 요약하여 일기로 써주며, 따뜻한 위로의 한마디를 건넵니다.

이 모든 과정은 **외부 API 호출 없이(Cost Zero)**, 사용자의 로컬 환경(Docker)에서 안전하게 수행됩니다.

## ✨ 주요 기능 (Key Features)
* **🎤 음성 기록 (STT)**: 빠르고 정확한 `Faster-Whisper` 모델이 당신의 목소리를 텍스트로 변환합니다.
* **🧠 감정 정밀 분석**: `mDeBERTa` 모델이 5가지 핵심 감정(기쁨, 슬픔, 분노, 불안, 평온)을 분석하고 수치화합니다.
* **✍️ AI 일기 & 제목 생성**: **LG EXAONE 3.0 (7.8B)** LLM이 구어체 기록을 차분한 문어체 일기로 다듬고, 하루를 은유하는 **감성 제목**을 지어줍니다.
* **💌 맞춤형 위로 메시지**: 분석된 감정과 내용을 바탕으로 심리 상담사 페르소나의 AI가 따뜻한 위로를 건넵니다.
* **📊 주간 리포트**: 사이드바에서 내 감정의 흐름과 빈도수를 시각화된 차트로 확인할 수 있습니다.
* **🔒 프라이버시 보호**: 모든 데이터는 내 컴퓨터(MySQL)에만 저장되며 외부로 유출되지 않습니다.

## 🛠️ 기술 스택 (Tech Stack)
| 구분 | 기술 | 역할 및 모델 |
| :--- | :--- | :--- |
| **Backend** | FastAPI (v3.12) | 비동기 API 서버, 백그라운드 태스크 관리 |
| **Frontend** | Streamlit | 반응형 대화형 UI, 실시간 데이터 시각화 (Altair) |
| **AI (STT)** | Faster-Whisper | `small` 모델 (Int8 Quantized) - 고속 음성 변환 |
| **AI (NLP)** | Transformers | `mDeBERTa-v3-base` - 제로샷 감정 분류 |
| **AI (LLM)** | **Llama.cpp (Python)** | **LG EXAONE 3.0 7.8B Instruct (GGUF)** - 일기/제목/위로 생성 |
| **Database** | MySQL 8.0 | 사용자 정보, 일기 데이터, 감정 분석 결과 저장 |
| **Infra** | Docker Compose | 서비스 전체 컨테이너 오케스트레이션 |

## 🏗️ 시스템 아키텍처 (Architecture)
1. **User**가 Streamlit UI를 통해 음성을 녹음 및 업로드.
2. **FastAPI** 서버가 요청을 받아 비동기 처리를 시작 (`202 Accepted`).
3. **STT Service**가 오디오를 텍스트로 변환 (WAV 16kHz 변환 포함).
4. **Emotion Service**가 텍스트에서 감정을 추출.
5. **Diary Service (LLM)**가 일기 본문 요약, 제목 창작, 위로 메시지를 생성.
6. 모든 결과는 **MySQL**에 저장되고, UI에서 Polling을 통해 실시간 완료 처리.

## 🏃 시작하기 (Quick Start)

### 권장 사양
* **RAM**: 16GB 이상 권장 (LLM 구동을 위해 최소 8GB 이상의 여유 메모리 필요)
* **Disk**: 약 10GB 여유 공간 (Docker 이미지 및 AI 모델 파일)

### 설치 및 실행

**1. 저장소 복제**
```bash
git clone [https://github.com/voice-journal/vench.git](https://github.com/voice-journal/vench.git)
cd vench
```
**2. 실행 (Docker Compose) 최초 실행 시 대용량 모델(LG EXAONE, 약 5GB+)을 다운로드하므로 시간이 소요될 수 있습니다.**
```bash
docker-compose up -d --build
```
**3. 접속**
```bash
Frontend: http://localhost:8501

Backend Docs: http://localhost:8000/docs
```

**⚠️ 초기화 방법 (데이터 삭제)**
```bash
# 1. 컨테이너 종료 및 DB 볼륨(데이터) 삭제
docker-compose down -v

# 2. (선택) 로컬에 생성된 데이터 폴더 정리
rm -rf data/mysql/* data/audio/*

# 🚨 주의: data/models 폴더는 절대 지우지 마세요! (모델을 다시 받아야 합니다)
```

