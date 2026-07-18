# player/input_handler.py
import pygame

class PlayerInputHandler:
    def __init__(self):
        self.mouse_left_was_pressed = False
        self.mouse_right_was_pressed = False

    def update(self, vars_obj, keys, dt=0.0):
        mouse_state = pygame.mouse.get_pressed()

        # ⚔️ 1-A. 좌클릭: 제자리 일반 공격 콤보 트랙 (NORMAL)
        if mouse_state[0]:
            if not self.mouse_left_was_pressed:
                cooldown = getattr(vars_obj, 'attack_cooldown_timer', 0.0)
                if cooldown <= 0.0:
                    self.trigger_attack(vars_obj, attack_mode="NORMAL")
            self.mouse_left_was_pressed = True
        else:
            self.mouse_left_was_pressed = False

        # ⚔️ 1-B. 우클릭: 독립된 단발성 돌진 공격 트랙 (DASH)
        if mouse_state[2]:
            if not self.mouse_right_was_pressed:
                cooldown = getattr(vars_obj, 'attack_cooldown_timer', 0.0)
                if cooldown <= 0.0:
                    self.trigger_attack(vars_obj, attack_mode="DASH")
            self.mouse_right_was_pressed = True
        else:
            self.mouse_right_was_pressed = False

        # 🏃 2. 키보드 이동 입력 상태 플래그 초기화
        vars_obj.is_moving = False

        # [무결성 수정] 시프트 키 분기
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            vars_obj.move_state = "RUN"
        else:
            vars_obj.move_state = "WALK"

        # 🎯 [무결성 수정] A/D 동시 입력 방지 (if-elif 구조 적용)
        # 이펙트 출력 및 공격 도중에도 사용자의 즉각적인 이동 전환 역동성을 보장하기 위해
        # 이동 입력 플래그(is_moving)와 시선 방향(facing_right) 전환 가드를 전면 개방합니다.
        if keys[pygame.K_a]:
            vars_obj.is_moving = True
            vars_obj.facing_right = False

        elif keys[pygame.K_d]:
            vars_obj.is_moving = True
            vars_obj.facing_right = True

        # 🚀 3. 점프 입력 제어 (공격 중 대각선 돌진 중일 때 점프가 입력되어 궤적이 깨지는 것을 안전 방지)
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and not vars_obj.is_jumping:
            # 돌진 공격 중에 강제 점프로 속도 벡터가 상충되지 않도록 가드
            if not vars_obj.is_attacking:
                vars_obj.vertical_velocity = -vars_obj.jump_power
                vars_obj.is_jumping = True

    def trigger_attack(self, vars_obj, attack_mode):
        # 공격 중인 애니메이션 세션이 도는 동안에는 중복 입력 방지
        if vars_obj.is_attacking:
            return

        vars_obj.is_attacking = True
        vars_obj.attack_mode = attack_mode

        if attack_mode == "NORMAL":
            # ⚔️ [OnHit 전용 콤보 전환] - 일반 공격 트랙 전용으로 완전 격리
            if getattr(vars_obj, 'combo_timer', 0) <= 0 or getattr(vars_obj, 'combo_step', 0) == 0:
                vars_obj.combo_step = 1
            else:
                if vars_obj.combo_step == 1:
                    vars_obj.combo_step = 2
                elif vars_obj.combo_step == 2:
                    vars_obj.combo_step = 3
                else:
                    vars_obj.combo_step = 1
            vars_obj.combo_timer = vars_obj.combo_expire_time
        else:
            # DASH 모드는 콤보 단계와 연동하지 않으며 단발성으로 작동
            vars_obj.combo_step = 0