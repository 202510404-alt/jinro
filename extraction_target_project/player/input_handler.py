# player/input_handler.py
import pygame

class PlayerInputHandler:
    def __init__(self):
        self.mouse_was_pressed = False # 마우스 단발성 클릭 체크용 변수

    def update(self, vars_obj, keys):
        # ⚔️ 1. 마우스 좌클릭 입력 상시 감지 (공격 중에도 연타 입력을 받을 수 있도록 최상단 배치)
        mouse_state = pygame.mouse.get_pressed()
        if mouse_state[0]:  
            if not self.mouse_was_pressed: 
                self.trigger_attack(vars_obj)
            self.mouse_was_pressed = True
        else:
            self.mouse_was_pressed = False

        # 🏃 2. 키보드 이동 입력 처리 (★공격 중이어도 이동이 끊기지 않도록 수정)
        keys = pygame.key.get_pressed()
        vars_obj.is_moving = False
        
        # 걷기/달리기 속도 설정
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            current_speed = vars_obj.run_speed
            vars_obj.move_state = "RUN"
        else:
            current_speed = vars_obj.walk_speed
            vars_obj.move_state = "WALK"

        # 🌟 핵심 수정: 공격 중일 때도 키보드 입력을 받아서 좌표를 움직여줍니다!
        if keys[pygame.K_a]:
            vars_obj.x -= current_speed
            vars_obj.is_moving = True
            # 단, 공격 애니메이션 재생 중에는 공격하는 방향을 유지하기 위해 바라보는 방향 전환을 막아줄 수 있습니다.
            # 공격 중에 뒤를 돌면 어색할 수 있으므로, 공격 중이 아닐 때만 방향 전환을 허용합니다.
            if not vars_obj.is_attacking:
                vars_obj.facing_right = False
                
        if keys[pygame.K_d]:
            vars_obj.x += current_speed
            vars_obj.is_moving = True
            if not vars_obj.is_attacking:
                vars_obj.facing_right = True

        # 점프 입력 (공격 중에도 점프가 가능하도록 유지)
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and not vars_obj.is_jumping:
            vars_obj.vertical_velocity = -vars_obj.jump_power
            vars_obj.is_jumping = True

    def trigger_attack(self, vars_obj):
        """공격 버튼을 눌렀을 때 실행되는 콤보 전환기"""
        if vars_obj.is_attacking:
            return

        vars_obj.is_attacking = True
        vars_obj.attack_timer = vars_obj.attack_duration 

        # 적 타격 여부에 따른 콤보 전환
        if vars_obj.combo_step == 1 and vars_obj.has_hit_enemy:
            vars_obj.combo_step = 2
        elif vars_obj.combo_step == 2 and vars_obj.has_hit_enemy:
            vars_obj.combo_step = 3
        else:
            vars_obj.combo_step = 1

        vars_obj.has_hit_enemy = False