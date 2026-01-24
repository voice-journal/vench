# 🛋️ Vench (Voice + Bench)
> "번아웃 온 당신, 30초만 털어놓으세요. 기록과 분석은 AI가 합니다."

## 🚀 시작하기 (Getting Started)
팀원들은 이 가이드를 따라 로컬 개발 환경을 세팅해주세요.

### 1️⃣ 필수 준비물 (Prerequisites)
* **Docker Desktop** (반드시 켜져 있어야 함)
* **Python 3.12**
* **Git**

### 2️⃣ 프로젝트 설치 (Installation)
터미널을 열고 순서대로 입력하세요.

```bash
# 1. 저장소 복제 (Clone)
git clone [https://github.com/voice-journal/vench.git](https://github.com/voice-journal/vench.git)
cd vench

# 2. 패키지 매니저 'uv' 설치 (이미 있으면 생략)
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# 3. 가상환경 생성 및 라이브러리 설치 (로컬 IDE용)
uv venv --python 3.12
source .venv/bin/activate
uv pip install pip  # IDE 인식용
uv pip install -r requirements.txt
