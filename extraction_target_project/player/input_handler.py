# player/input_handler.py
import pygame

class PlayerInputHandler:
    def __init__(self):
        self.mouse_was_pressed = False # 마우스 단발성 클릭 체크용 변수

    def update(self, vars_obj, keys):
        # ⚔️ 1. 마우스 좌클릭 입력 상시 감지 (공격 중에도 연타 입력을 누락 없이 체크하기 위해 최상단 배치)
        mouse_state = pygame.mouse.get_pressed()
        if mouse_state[0]:  
            if not self.mouse_was_pressed: 
                self.trigger_attack(vars_obj)
            self.mouse_was_pressed = True
        else:
            self.mouse_was_pressed = False

        # 🏃 2. 키보드 이동 입력 상태 플래그 초기화
        vars_obj.is_moving = False
        
        # 🎯 [누락 및 변조 수정] 외부 매개변수 keys를 강제로 덮어쓰던 하드코딩 라인을 제거하여
        # 상위 엔진 프레임워크와의 유기적 캡슐화와 연출 시 조작 차단 인터페이스를 완벽히 확보
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            vars_obj.move_state = "RUN"
        else:
            vars_obj.move_state = "WALK"

        # 🎯 [물리 무결성 수정] vars_obj.x 좌표 직접 변조 완전 제거
        # 입력 핸들러는 의도와 방향 플래그만 변경하고, 실제 가변 이동은 player_main.py에서 dt와 안전하게 융합됩니다.
        if keys[pygame.K_a]:
            vars_obj.is_moving = True
            if not vars_obj.is_attacking:
                vars_obj.facing_right = False
                
        if keys[pygame.K_d]:
            vars_obj.is_moving = True
            if not vars_obj.is_attacking:
                vars_obj.facing_right = True

        # 점프 입력 신호 감지 (이동 물리 엔진에 트리거 전달)
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and not vars_obj.is_jumping:
            vars_obj.vertical_velocity = -vars_obj.jump_power
            vars_obj.is_jumping = True

    def trigger_attack(self, vars_obj):
        """공격 버튼을 눌렀을 때 실행되는 콤보 전환 프로세서"""
        if vars_obj.is_attacking:
            return

        vars_obj.is_attacking = True
        vars_obj.attack_timer = vars_obj.attack_duration 

        # 🎯 [누락 해결] 콤보 유효 시간(combo_timer) 및 콤보 초기화 분기를 완벽하게 정렬하여 연동 실패 차단
        if getattr(vars_obj, 'combo_timer', 0) <= 0:
            vars_obj.combo_step = 1
        else:
            # 적 타격 성공 여부에 따른 체인 콤보 연계 단계 연산
            if vars_obj.combo_step == 1 and vars_obj.has_hit_enemy:
                vars_obj.combo_step = 2
            elif vars_obj.combo_step == 2 and vars_obj.has_hit_enemy:
                vars_obj.combo_step = 3
            else:
                vars_obj.combo_step = 1

        # 콤보 작동 성공 시 유효 만료 시간 최신화 및 타격 버퍼 리셋
        vars_obj.combo_timer = getattr(vars_obj, 'combo_expire_time', 90)
        vars_obj.has_hit_enemy = False