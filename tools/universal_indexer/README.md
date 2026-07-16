# 🚀 Jjap-Cursor Codebase Tools (Roo Code Context Surgeon V2)

형님(AI Agent 및 개발자)의 개발 생산성을 극대화하고, LLM(Gemini/Claude 등)의 토큰 낭비를 0%로 수렴시키기 위해 설계된 **실시간 코드베이스 인덱싱 및 정밀 컨텍스트 추출 시스템**입니다.

이 시스템은 코드 변경 사항을 백그라운드에서 실시간으로 감시하고, 클래스 및 함수의 의존성 관계(Skeleton, Calls, Used By)를 자동으로 정립하며, AI 프롬프트에 불필요한 설명 주석 및 로그 블록을 검열하여 오직 순수한 핵심 로직(Raw Pure Logic)만 보따리에 싸서 전달합니다.

---

## 📜 4대 절대 코드 규칙 (Core Protocols)

본 프로젝트의 모든 코드는 아래 4가지 철칙을 칼같이 준수하며 동작합니다.

1. **🧩 1파일 1심볼 극단 분리 규칙**: 하나의 파이썬 파일에는 단 하나의 명확한 함수 또는 단일 책임을 지는 1개의 클래스만 존재하도록 격리합니다. 파일명이 곧 함수의 이름이자 역할이 됩니다.
2. **🎛️ On/Off 디버깅 로그 도배 규칙**: `DEBUG_MODE = True/False` 원터치 스위치를 장착하여 에러 발생 시 핀포인트 추적이 가능하도록 로그를 촘촘히 도배합니다.
3. **📝 주석의 엄격한 이원화 및 검열**: 
   - `# HISTORY:` (AI 오답노트): 과거 오류와 해결 방법을 압축 기록하여 LLM에게 상시 배송합니다.
   - `# INFO:` (개발자 전용 설명서): 개발자용 친절한 설명이며, AI에게 배송될 때는 흔적도 없이 도려내집니다.
   - ⚡ `context_builder.py` 작동 시 `# INFO:` 주석뿐만 아니라 `if DEBUG_MODE:` 블록 전체를 증발시켜 AI에게 극단적인 압축 컨텍스트를 제공합니다.
4. **🎯 초심 유지 규칙**: "최소 토큰 최대 맥락", "Core-First (UI 분리)", "Safety-First" 철학을 100% 반영합니다.

---

## 🛠️ 시스템 요구 사항 (System Requirements)

- **Python 버전**: `Python 3.10` 이상 권장 (최소 3.8 이상 필요)
- **운영체제**: Windows, macOS, Linux 공용

---

## 📦 필수 외부 라이브러리 및 설치 (Dependencies)

```bash
# 가상환경 활성화 후 실행
pip install --upgrade pip
pip install watchdog