# player/input_handler.py
import pygame


class PlayerInputHandler:
    def __init__(self):
        # 좌/우클릭을 각각 단발성으로 판정하기 위한 분리된 상태 플래그
        self.mouse_left_was_pressed = False
        self.mouse_right_was_pressed = False

    def update(self, vars_obj, keys, dt=0.0):
        mouse_state = pygame.mouse.get_pressed()

        # ⚔️ 1-A. 좌클릭: 2배 거리 자동 타겟팅이 조건부로 작동하는 공격 입력
        if mouse_state[0]:
            if not self.mouse_left_was_pressed:
                cooldown = getattr(vars_obj, 'attack_cooldown_timer', 0.0)
                if cooldown <= 0.0:
                    self.trigger_attack(vars_obj, is_targeting_click=True)
            self.mouse_left_was_pressed = True
        else:
            self.mouse_left_was_pressed = False

        # ⚔️ 1-B. 우클릭: 자동 타겟팅을 사용하지 않는 비타겟팅 고정 공격 입력
        if mouse_state[2]:
            if not self.mouse_right_was_pressed:
                cooldown = getattr(vars_obj, 'attack_cooldown_timer', 0.0)
                if cooldown <= 0.0:
                    self.trigger_attack(vars_obj, is_targeting_click=False)
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

    def trigger_attack(self, vars_obj, is_targeting_click):
        # 공격 중인 애니메이션 세션이 도는 동안에는 중복 입력 방지
        if vars_obj.is_attacking:
            return

        vars_obj.is_attacking = True
        # 이번 타수가 좌클릭(자동 타겟팅) 유래인지, 우클릭(비타겟팅 고정) 유래인지 기록
        vars_obj.is_targeting = is_targeting_click

        # ⚔️ [OnHit 전용 콤보 전환]
        # combat_processor.process()는 직전 타수가 적을 맞추지 못했을 경우(has_hit_enemy == False)
        # 정산 시점에 combo_step을 반드시 0으로 되돌려 놓는다.
        # 따라서 여기서는 combo_step이 0인지(=직전 타수가 적중하지 못했거나 최초 공격)만 검사하면
        # "적중 시에만 다음 타수로 전환"이라는 스펙이 자연스럽게 보장된다.
        if getattr(vars_obj, 'combo_timer', 0) <= 0 or vars_obj.combo_step == 0:
            vars_obj.combo_step = 1
        else:
            if vars_obj.combo_step == 1:
                vars_obj.combo_step = 2
            elif vars_obj.combo_step == 2:
                vars_obj.combo_step = 3
            else:
                vars_obj.combo_step = 1

        vars_obj.combo_timer = vars_obj.combo_expire_time
