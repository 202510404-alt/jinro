# src/dialogue_system/dialogue_manager.py
import pygame
import os
import json
from map_system.map_engine import AssetManager

class DialogueManager:
    """
    독립형 대사 시스템 엔진 (DialogueManager)
    대사 데이터를 캐싱 및 노드별로 제어하며 월드 정지 상태 제어 인터페이스를 지원합니다.
    """
    def __init__(self):
        self.dialogues = {}
        self.current_sequence = None
        self.current_index = 0
        self.is_active = False

        # 폰트 초기화 (한글 출력을 위해 나눔고딕, 맑은 고딕, 혹은 기본 폰트 바인딩)
        pygame.font.init()
        font_names = ["malgungothic", "nanumgothic", "nanumbrushouter", "notosanskorean", "arial", None]
        self.font_speaker = None
        self.font_text = None
        
        # 순차적으로 사용 가능한 한글 폰트 검색 및 초기화
        for f_name in font_names:
            try:
                self.font_speaker = pygame.font.SysFont(f_name, 32, bold=True)
                self.font_text = pygame.font.SysFont(f_name, 28)
                break
            except Exception:
                continue
        
        # 폴백 설정
        if not self.font_speaker:
            self.font_speaker = pygame.font.Font(None, 36)
            self.font_text = pygame.font.Font(None, 30)

        # 리소스 경로 자동 해결용 base_dir
        self.src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def load_dialogues(self, json_path=None):
        """대사 정보 캐싱"""
        if json_path is None:
            json_path = os.path.join(self.src_dir, "assets", "data", "dialogues.json")
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self.dialogues = json.load(f)
            print(f"📖 [DialogueManager] {len(self.dialogues)}개의 대사 시퀀스를 성공적으로 로드했습니다.")
        except Exception as e:
            print(f"🚨 [DialogueManager] 대사 파일 로드 에러: {e}")
            self.dialogues = {}

    def start_dialogue(self, dialogue_id):
        """특정 대사 시퀀스 가동"""
        if dialogue_id not in self.dialogues:
            print(f"⚠️ [DialogueManager] 알 수 없는 대사 ID: {dialogue_id}")
            return False

        self.current_sequence = self.dialogues[dialogue_id]
        self.current_index = 0
        self.is_active = True
        print(f"💬 [DialogueManager] 대사 시작 -> ID: '{dialogue_id}' (총 {len(self.current_sequence)}줄)")
        
        # 첫 라인 이벤트/액션 감지 시 즉시 처리
        self._trigger_current_action()
        return True

    def next_line(self):
        """다음 대사로 진행"""
        if not self.is_active or not self.current_sequence:
            return

        self.current_index += 1
        if self.current_index >= len(self.current_sequence):
            self.end_dialogue()
        else:
            self._trigger_current_action()

    def end_dialogue(self):
        """대사 시퀀스 완료 및 비활성화"""
        self.current_sequence = None
        self.current_index = 0
        self.is_active = False
        print("💬 [DialogueManager] 대사 종료 -> 인게임 월드 정상 재개")

    def _trigger_current_action(self):
        """대사 노드에 부여된 특수 연출 액션 실행 구조"""
        if not self.current_sequence or self.current_index >= len(self.current_sequence):
            return
        node = self.current_sequence[self.current_index]
        action = node.get("action")
        if action:
            # Main이나 다른 시스템에서 받아 처리하도록 로그 혹은 이벤트 발행 구조로 설계
            print(f"🎬 [DialogueAction] 연출 트리거: {action}")

    def draw(self, screen):
        """대사창 UI 렌더링"""
        if not self.is_active or not self.current_sequence:
            return

        node = self.current_sequence[self.current_index]
        speaker = node.get("speaker", "???")
        text = node.get("text", "")
        portrait_key = node.get("portrait", "")

        # 1. 반투명 배경 대사 상자 (Virtual 해상도 1600x1200 기준 하단 배치)
        box_rect = pygame.Rect(100, 850, 1400, 300)
        
        # 반투명 효과를 위해 별도 서피스 사용
        box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        box_surf.fill((20, 20, 30, 230))  # 짙은 남색 반투명
        pygame.draw.rect(box_surf, (150, 180, 220, 255), (0, 0, box_rect.width, box_rect.height), 4) # 하늘색 테두리
        screen.blit(box_surf, (box_rect.x, box_rect.y))

        # 2. 초상화 로드 (AssetManager를 무조건적으로 연동)
        portrait_path = os.path.join(self.src_dir, "assets", "images", "portraits", f"{portrait_key}.png")
        portrait_img = AssetManager.get_image(portrait_path)
        
        # 초상화 200x200으로 스케일링 후 배치
        scaled_portrait = pygame.transform.scale(portrait_img, (200, 200))
        screen.blit(scaled_portrait, (150, 900))

        # 3. 화자 이름 드로우
        speaker_surf = self.font_speaker.render(speaker, True, (255, 230, 150))
        screen.blit(speaker_surf, (380, 890))

        # 4. 말풍선 내 한국어 자동 줄바꿈(Text Wrapping) 및 렌더링
        max_text_w = 1050
        wrapped_lines = self._wrap_text(text, self.font_text, max_text_w)
        
        y_offset = 945
        for line in wrapped_lines:
            line_surf = self.font_text.render(line, True, (240, 240, 250))
            screen.blit(line_surf, (380, y_offset))
            y_offset += 40

        # 5. 다음 대사 지시자 표시 (깜빡이는 연출 생략용 고정 키 가이드)
        prompt_surf = self.font_text.render("[ Space or Enter ]", True, (150, 180, 220))
        screen.blit(prompt_surf, (1300, 1100))

    def _wrap_text(self, text, font, max_width):
        """글자 너비 기반 한국어 글자 단위 자동 줄바꿈 알고리즘"""
        lines = []
        current_line = ""
        for char in text:
            test_line = current_line + char
            width, _ = font.size(test_line)
            if width > max_width:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        return lines
