# player/input_handler.py
import pygame

class PlayerInputHandler:
    def __init__(self):
        self.mouse_was_pressed = False # 마우스 단발성 클릭 체크용 변수

    def update(self, vars_obj, keys, dt=0.0):
        # ⚔️ 1. 마우스 좌클릭 입력 및 쿨타임 검증
        # 쿨타임 타이머(attack_cooldown_timer)가 0 이하일 때만 신규 공격 트리거 허용
        mouse_state = pygame.mouse.get_pressed()
        if mouse_state[0]:  
            if not self.mouse_was_pressed: 
                cooldown = getattr(vars_obj, 'attack_cooldown_timer', 0.0)
                if cooldown <= 0.0:
                    self.trigger_attack(vars_obj)
            self.mouse_was_pressed = True
        else:
            self.mouse_was_pressed = False

        # 🏃 2. 키보드 이동 입력 상태 플래그 초기화
        vars_obj.is_moving = False
        
        # [무결성 수정] 시프트 키 분기
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            vars_obj.move_state = "RUN"
        else:
            vars_obj.move_state = "WALK"

        # 🎯 [무결성 수정] A/D 동시 입력 방지 (if-elif 구조 적용)
        # 공격 중(`is_attacking`)일 때는 시선 방향(facing_right) 전환을 차단하여 돌진 방향 유지
        if keys[pygame.K_a]:
            vars_obj.is_moving = True
            if not vars_obj.is_attacking:
                vars_obj.facing_right = False
                
        elif keys[pygame.K_d]:
            vars_obj.is_moving = True
            if not vars_obj.is_attacking:
                vars_obj.facing_right = True

        # 🚀 3. 점프 입력 제어 (공격 중 대각선 돌진 중일 때 점프가 입력되어 궤적이 깨지는 것을 안전 방지)
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and not vars_obj.is_jumping:
            # 돌진 공격 중에 강제 점프로 속도 벡터가 상충되지 않도록 가드
            if not vars_obj.is_attacking:
                vars_obj.vertical_velocity = -vars_obj.jump_power
                vars_obj.is_jumping = True

    def trigger_attack(self, vars_obj):
        # 공격 중인 애니메이션 세션이 도는 동안에는 중복 입력 방지
        if vars_obj.is_attacking:
            return

        vars_obj.is_attacking = True
        
        # 콤보 판정 흐름 설계 (has_hit_enemy 조건과 무관하게 타이머 범위 내 클릭 시 부드럽게 전이)
        if getattr(vars_obj, 'combo_timer', 0) <= 0:
            vars_obj.combo_step = 1
        else:
            if vars_obj.combo_step == 1:
                vars_obj.combo_step = 2
            elif vars_obj.combo_step == 2:
                vars_obj.combo_step = 3
            else:
                vars_obj.combo_step = 1

        vars_obj.combo_timer = vars_obj.combo_expire_time