# src/main.py
import pygame
import sys
import os
from player.player_main import Player


from settings import SCREEN_WIDTH, SCREEN_HEIGHT, VIRTUAL_WIDTH, VIRTUAL_HEIGHT, FPS, GROUND_Y
from player.player_main import Player
from map_system.map_main import GameMap
from camera import ElasticCamera
from dialogue_system.dialogue_manager import DialogueManager

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
# 그 상위 폴더(jinro 등)나 프로젝트 루트도 인식할 수 있게 안전망으로 등록
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 카메라 및 시스템 세팅 상수 안전망 정의
CAMERA_SMOOTHING = 0.05
CAMERA_DEADZONE_W = 100
CAMERA_DEADZONE_H = 80
CAMERA_MAX_SPEED_PX_PER_Sec = None

class AppState:
    MAIN_MENU = "MAIN_MENU"
    GAME_PLAY = "GAME_PLAY"
    MAP_EDITOR = "MAP_EDITOR"

def draw_player_hp_hud(surface, player_obj):
    """
    플레이어 HP HUD 표시 (순정 사양 준수 및 비주얼 게이지 적용)
    """
    if hasattr(player_obj, 'vars') and hasattr(player_obj.vars, 'hp'):
        # 1. 기존 데이터 프로토콜 안전하게 참조
        hp = player_obj.vars.hp
        max_hp = getattr(player_obj.vars, 'max_hp', 100) # 안전장치: 없을 경우 100 기본값
        
        # 2. HP 비율 계산 (0.0 ~ 1.0 제한)
        hp_ratio = max(0.0, min(1.0, float(hp) / float(max_hp)))
        
        # 3. HUD 위치 및 크기 정의 (왼쪽 위 배치)
        hud_x, hud_y = 20, 20
        bar_width, bar_height = 200, 20
        border_thickness = 2
        
        # 4. 체력바 배경 (어두운 회색/검은색 테두리 배경)
        bg_rect = pygame.Rect(hud_x, hud_y, bar_width, bar_height)
        pygame.draw.rect(surface, (30, 41, 59), bg_rect)  # Slate 800 배경색
        
        # 5. 체력바 채우기 (현재 체력 비율 적용)
        # 체력이 낮아질수록 초록색(안전) -> 노란색(경고) -> 빨간색(위험)으로 보간 연산
        if hp_ratio > 0.5:
            bar_color = (34, 197, 94)  # 초록색 (Green 500)
        elif hp_ratio > 0.2:
            bar_color = (234, 179, 8)  # 노란색 (Yellow 500)
        else:
            bar_color = (239, 68, 68)  # 빨간색 (Red 500)
            
        fill_width = int(bar_width * hp_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(hud_x, hud_y, fill_width, bar_height)
            pygame.draw.rect(surface, bar_color, fill_rect)
            
        # 6. 체력바 외곽 테두리선 그리기
        border_rect = pygame.Rect(hud_x, hud_y, bar_width, bar_height)
        pygame.draw.rect(surface, (255, 255, 255), border_rect, border_thickness, border_radius=3)
        
        # 7. 수치 텍스트 오버레이 (바 중앙 혹은 오른쪽에 가독성 높게 출력)
        try:
            font = pygame.font.SysFont("malgungothic", 14, bold=True)
        except Exception:
            font = pygame.font.SysFont(None, 18, bold=True)
            
        text_surf = font.render(f"{hp} / {max_hp}", True, (255, 255, 255))
        # 검은색 텍스트 테두리(그림자) 효과로 시인성 극대화
        shadow_surf = font.render(f"{hp} / {max_hp}", True, (0, 0, 0))
        
        text_x = hud_x + bar_width + 10
        text_y = hud_y + (bar_height - text_surf.get_height()) // 2
        
        surface.blit(shadow_surf, (text_x + 1, text_y + 1))
        surface.blit(text_surf, (text_x, text_y))

def run_game(window_screen, virtual_screen, clock):
     """실제 인게임 액션 플레이 모드 루프 (AI 오염 제거 및 멀티맵 동적 락 장착)"""
     
     # 1. 객체 초기화 (기존 데이터 프로토콜 엄격 준수)
     player = Player(100, GROUND_Y - 60)
     game_map = GameMap(map_id=1)
     
     dialogue_manager = DialogueManager()
     dialogue_manager.load_dialogues()
     
     def start_dialogue_handler(action):
         dialogue_id = action.get("dialogue_id")
         dialogue_manager.start_dialogue(dialogue_id)
         
     game_map.register_action_handler("start_dialogue", start_dialogue_handler)
     dialogue_manager.start_dialogue("stage1_start_chat")
     
     # 2. 순정 카메라 엔진 셋업
     camera = ElasticCamera(
         VIRTUAL_WIDTH, VIRTUAL_HEIGHT,
         smoothing=CAMERA_SMOOTHING,
         deadzone_w=CAMERA_DEADZONE_W,
         deadzone_h=CAMERA_DEADZONE_H,
         max_speed_px_per_sec=None,
     )
     camera.set_center(player.vars.x + player.vars.width / 2.0, player.vars.y + player.vars.height / 2.0)
     
     # 3. 게임 메인 루프
     while True:
         dt = clock.tick(FPS) / 1000.0
         
         for event in pygame.event.get():
             if event.type == pygame.QUIT:
                 return None
             elif event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_ESCAPE:
                     return AppState.MAIN_MENU
                 if dialogue_manager.is_active and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    dialogue_manager.next_line()
                    
        # 대화창이 꺼져있을 때만 물리 및 업데이트 작동
         if not dialogue_manager.is_active:
            # 델타 타임(dt)과 적 목록(game_map.entities)을 함께 넘겨주어 정밀 물리와 타격을 작동시킵니다.
# 만약 main.py 내부의 루프에 dt 변수명이 다르게 되어있다면(예: deltatime 등) 해당 변수명으로 넣어주세요.
            dt = clock.get_time() / 1000.0  # 혹시 루프 내에 dt 정의가 없다면 이 줄을 위에 추가하세요.
            player.update_with_dt(game_map.platforms, game_map, dt, entities=game_map.entities)
            game_map.update(dt, player_obj=player)
            
            # 카메라 타겟 중심점 계산
            target_cx = float(player.vars.x + player.vars.width / 2.0)
            target_cy = float(player.vars.y + player.vars.height / 2.0)
            
            # [💡 형님의 매서운 지적 완벽 반영: JSON 멀티맵 동적 바닥 연동]
            # 하드코딩 600을 완전히 제거하고, JSON에서 파싱해온 맵의 바닥 높이를 실시간 추적합니다.
            dynamic_ground_y = float(game_map.ground_y) if hasattr(game_map, 'ground_y') else float(GROUND_Y)
            
            # 카메라가 화면 하단 한계선을 넘어 맵 바깥(땅 에셋 밑바닥 허공)을 보지 못하게 완벽 락(Lock)
            clamp_cam_y_max = float(game_map.ground_y) - (float(VIRTUAL_HEIGHT) / 2.0) + 30.0
            
            # 카메라 동적 업데이트 실행
            camera.update(target_cx, target_cy, dt, clamp_y_max=clamp_cam_y_max)
            
        # 4. 렌더링 파이프라인 (카메라 오프셋 적용)
         camera_offset = camera.get_offset()
         virtual_screen.fill((0, 0, 0))
        
        # 맵, 플레이어, HUD 그리기
         game_map.draw(virtual_screen, camera_offset=camera_offset)
         player.draw(virtual_screen, camera_offset=camera_offset)
         draw_player_hp_hud(virtual_screen, player)
        
         if dialogue_manager.is_active:
            dialogue_manager.draw(virtual_screen)
            
        # 가상 화면을 실제 윈도우 스크린 크기에 맞게 업스케일링 블릿
         scaled_surf = pygame.transform.scale(virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
         window_screen.blit(scaled_surf, (0, 0))
         pygame.display.flip()

def run_main_menu(window_screen, virtual_screen, clock):
    """메인 메뉴 루프 (순정 사양 복구 및 수려한 디자인 제공)"""
    pygame.display.set_caption("Jjap Cursor Game Engine - Main Menu")
    
    # 폰트 로딩 (한글 및 영문 텍스트 지원)
    try:
        title_font = pygame.font.SysFont("malgungothic", 72, bold=True)
        menu_font = pygame.font.SysFont("malgungothic", 36)
        info_font = pygame.font.SysFont("malgungothic", 24)
    except Exception:
        title_font = pygame.font.SysFont(None, 72, bold=True)
        menu_font = pygame.font.SysFont(None, 36)
        info_font = pygame.font.SysFont(None, 24)
        
    import math
    time_elapsed = 0.0
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        time_elapsed += dt
        
        # 키보드 이벤트 처리 및 락 해제
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    return AppState.GAME_PLAY
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    return AppState.MAP_EDITOR
                elif event.key == pygame.K_ESCAPE:
                    return None
                    
        # 가상 화면 렌더링 시작 (풍부하고 고급스러운 테마)
        virtual_screen.fill((15, 23, 42))  # Slate 900
        
        # 그리드 패턴 렌더링 (미학적 디테일)
        grid_size = 80
        grid_color = (30, 41, 59)
        for x in range(0, VIRTUAL_WIDTH, grid_size):
            pygame.draw.line(virtual_screen, grid_color, (x, 0), (x, VIRTUAL_HEIGHT))
        for y in range(0, VIRTUAL_HEIGHT, grid_size):
            pygame.draw.line(virtual_screen, grid_color, (0, y), (VIRTUAL_WIDTH, y))
            
        # 타이틀 텍스트 애니메이션 (사인파를 활용한 맥동)
        pulse_val = math.sin(time_elapsed * 3.0) * 8.0
        
        # 타이틀 글로우/그림자 효과
        shadow_surf = title_font.render("Jjap Cursor Game Engine", True, (56, 189, 248))  # Sky 400
        shadow_rect = shadow_surf.get_rect(center=(VIRTUAL_WIDTH // 2 - 4, 300 + int(pulse_val) - 4))
        virtual_screen.blit(shadow_surf, shadow_rect)
        
        title_surf = title_font.render("Jjap Cursor Game Engine", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(VIRTUAL_WIDTH // 2, 300 + int(pulse_val)))
        virtual_screen.blit(title_surf, title_rect)
        
        # 메뉴 박스 디자인
        btn_w, btn_h = 560, 90
        btn_x = (VIRTUAL_WIDTH - btn_w) // 2
        
        # 1: START GAME 버튼
        rect1 = pygame.Rect(btn_x, 520, btn_w, btn_h)
        pygame.draw.rect(virtual_screen, (30, 41, 59), rect1, border_radius=12)
        pygame.draw.rect(virtual_screen, (129, 140, 248), rect1, 3, border_radius=12)  # Indigo 400 Border
        text1 = menu_font.render("1: START GAME", True, (243, 244, 246))
        text1_rect = text1.get_rect(center=rect1.center)
        virtual_screen.blit(text1, text1_rect)
        
        # 2: MAP EDITOR 버튼
        rect2 = pygame.Rect(btn_x, 650, btn_w, btn_h)
        pygame.draw.rect(virtual_screen, (30, 41, 59), rect2, border_radius=12)
        pygame.draw.rect(virtual_screen, (16, 185, 129), rect2, 3, border_radius=12)  # Emerald 500 Border
        text2 = menu_font.render("2: MAP EDITOR", True, (243, 244, 246))
        text2_rect = text2.get_rect(center=rect2.center)
        virtual_screen.blit(text2, text2_rect)
        
        # 조작 가이드 메시지
        info_text = info_font.render("Press KEY 1 or 2 to select option, ESC to Quit", True, (148, 163, 184))
        info_rect = info_text.get_rect(center=(VIRTUAL_WIDTH // 2, 820))
        virtual_screen.blit(info_text, info_rect)
        
        # 가상 화면 스케일 업 블릿
        scaled_surf = pygame.transform.scale(virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
        window_screen.blit(scaled_surf, (0, 0))
        pygame.display.flip()

def draw(self, screen, camera_offset=(0, 0)):
        """플레이어 본체 이미지와 공격 시 쇠파이프 콤보 이펙트를 화면에 렌더링합니다."""
        ox, oy = camera_offset
        # 🎬 1. 캐릭터 본체 스프라이트 시퀀스 추출 및 출력 (기존 순정 로직 완벽 보존)
        anim_list = self.assets.images.get(self.vars.current_state, [])
        if not anim_list:
            return
            
        # 혹시 모를 인덱스 바운드 에러를 막기 위한 최종 안전 필터링
        idx = min(self.vars.current_frame_idx, len(anim_list) - 1)
        player_image = anim_list[idx]
        
        # 왼쪽을 바라보고 있다면 이미지 좌우 반전
        if not self.vars.facing_right:
            player_image = pygame.transform.flip(player_image, True, False)
            
        screen.blit(player_image, (self.vars.x - ox, self.vars.y - oy))
        
        # ─────────────────────────────────────────────────────────────
        # 🎯 [새로운 시스템 추가] 쇠파이프 타격 범위(이펙트) 가시화 및 콤보별 연출
        # ─────────────────────────────────────────────────────────────
        if getattr(self.vars, 'is_attacking', False) and getattr(self.vars, 'attack_rect', None):
            # 카메라 좌표계가 반영된 실시간 이펙트 렌더링 사각형 변환
            eff_rect = pygame.Rect(
                self.vars.attack_rect.x - ox,
                self.vars.attack_rect.y - oy,
                self.vars.attack_rect.width,
                self.vars.attack_rect.height
            )
            
            # 투명도(Alpha) 표현이 가능한 이펙트 전용 특수 표면(Surface) 생성 (최적화 결합)
            effect_surf = pygame.Surface((eff_rect.width, eff_rect.height), pygame.SRCALPHA)
            
            # 현재 콤보 단수(1타, 2타, 3타막타)에 맞춰 시각 효과 가변 분기
            combo = getattr(self.vars, 'combo_step', 1)
            if combo == 1:
                # 1타: 신속하게 파고드는 블루 화이트 타격 잔상 (반투명)
                color = (52, 152, 219, 140) 
                pygame.draw.ellipse(effect_surf, color, (0, 0, eff_rect.width, eff_rect.height))
            elif combo == 2:
                # 2타: 좌우 반전 궤적으로 휘두르는 날카로운 옐로우 타격 잔상
                color = (241, 196, 15, 140)
                pygame.draw.ellipse(effect_surf, color, (0, 0, eff_rect.width, eff_rect.height))
            elif combo == 3:
                # 3타: 제자리 고정 묵직한 오렌지-레드 대형 광역 내려찍기 충격파 연출
                color = (231, 76, 60, 180)
                # 바닥 충격파 영역 생성
                pygame.draw.rect(effect_surf, color, (0, 0, eff_rect.width, eff_rect.height), border_radius=8)
                # 크래시 방지 및 시인성을 위한 내부 화이트 하이라이트 테두리 선 추가
                pygame.draw.rect(effect_surf, (255, 255, 255, 220), (0, 0, eff_rect.width, eff_rect.height), 3, border_radius=8)
                
            # 최종 연산 완료된 이펙트를 게임 화면에 블릿(Blit) 출력
            screen.blit(effect_surf, (eff_rect.x, eff_rect.y))

def main():
    """게임 진입점"""
    pygame.init()
    pygame.display.set_caption("Jjap Cursor Game Engine")
    
    window_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    clock = pygame.time.Clock()
    
    current_state = AppState.MAIN_MENU
    
    while current_state is not None:
        if current_state == AppState.MAIN_MENU:
            current_state = run_main_menu(window_screen, virtual_screen, clock)
        elif current_state == AppState.GAME_PLAY:
            current_state = run_game(window_screen, virtual_screen, clock)
        elif current_state == AppState.MAP_EDITOR:
            from map_editor_tool.map_editor import MapEditor
            editor = MapEditor()
            current_state = editor.run(window_screen, virtual_screen, clock)
        else:
            break
            
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()