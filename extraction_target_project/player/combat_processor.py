# [📂 player/combat_processor.py]
import pygame
import math

class PlayerCombatProcessor:
    def __init__(self):
        pass

    def process(self, vars_obj, entities=None, dt=0.0):
        # 안전장치: 변수 객체에 쿨타임 필드가 없을 경우 동적 확보
        if not hasattr(vars_obj, 'attack_cooldown_timer'):
            vars_obj.attack_cooldown_timer = 0.0

        # 1. 공격 불가(쿨타임) 실시간 감쇄 연산
        if vars_obj.attack_cooldown_timer > 0.0:
            vars_obj.attack_cooldown_timer -= dt
            if vars_obj.attack_cooldown_timer < 0.0:
                vars_obj.attack_cooldown_timer = 0.0

        # 2. 새로운 공격 모션 프레임 개시 시점
        if vars_obj.is_attacking and getattr(vars_obj, 'attack_timer', 0) == 0:
            if not hasattr(vars_obj, 'combo_step') or vars_obj.combo_step == 0:
                vars_obj.combo_step = 1

            # 🎯 [타겟팅] 플레이어에게 가장 가까운 유효 적 탐색 (사거리 제한 완화)
            target_enemy = None
            max_target_distance = vars_obj.attack_range_width * 3.0  # 더 넓은 범위의 타겟 서칭 허용
            min_dist_sq = max_target_distance * max_target_distance
            
            if entities:
                for entity in entities:
                    if entity == self or getattr(entity, 'vars', None) == vars_obj:
                        continue
                    e_vars = getattr(entity, 'vars', None)
                    if not e_vars or getattr(e_vars, 'is_dead', False):
                        continue
                    
                    dx = e_vars.x - vars_obj.x
                    dy = e_vars.y - vars_obj.y
                    dist_sq = dx*dx + dy*dy
                    
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        target_enemy = entity

            # 3. 콤보 분기 및 돌진 속도 적용 (★ 대시 길이를 기존의 10분의 1인 75.0 수준으로 조절)
            dash_speed = 75.0  # 750.0에서 10분의 1로 급감하여 짧고 조작 가능한 대시로 변경
            vars_obj.attack_timer = 12 if vars_obj.combo_step in [1, 2] else 18
            
            if vars_obj.combo_step == 1:
                # [1타] 적을 향해 가볍고 짧은 추적 돌진
                if target_enemy:
                    te_vars = target_enemy.vars
                    dx = te_vars.x - vars_obj.x
                    dy = te_vars.y - vars_obj.y
                    dist = math.sqrt(dx*dx + dy*dy) if (dx*dx + dy*dy) > 0 else 1.0
                    
                    vars_obj.facing_right = (dx > 0)
                    y_margin = 25
                    
                    if abs(dy) > y_margin:
                        vars_obj.vx = (dx / dist) * dash_speed
                        vars_obj.vy = (dy / dist) * dash_speed
                    else:
                        vars_obj.vx = dash_speed if dx > 0 else -dash_speed
                        vars_obj.vy = 0
                else:
                    vars_obj.vx = dash_speed if vars_obj.facing_right else -dash_speed
                    vars_obj.vy = 0

            elif vars_obj.combo_step == 2:
                # [2타] 적을 관통하거나 뒤로 짧게 빠지는 역돌진
                if target_enemy:
                    te_vars = target_enemy.vars
                    dx = te_vars.x - vars_obj.x
                    dy = te_vars.y - vars_obj.y
                    dist = math.sqrt(dx*dx + dy*dy) if (dx*dx + dy*dy) > 0 else 1.0
                    
                    vars_obj.facing_right = (dx > 0)
                    y_margin = 25
                    
                    if abs(dy) > y_margin:
                        vars_obj.vx = (dx / dist) * dash_speed
                        vars_obj.vy = (dy / dist) * dash_speed
                    else:
                        vars_obj.vx = dash_speed if dx > 0 else -dash_speed
                        vars_obj.vy = 0
                else:
                    vars_obj.facing_right = not vars_obj.facing_right
                    vars_obj.vx = dash_speed if vars_obj.facing_right else -dash_speed
                    vars_obj.vy = 0

            elif vars_obj.combo_step == 3:
                # [3타] 제자리 제어 공격
                vars_obj.vx = 0
                vars_obj.vy = 0

            vars_obj.has_hit_enemy = False

        # 4. 공격 액션 진행 중 (★ 콤보 시 조작감 쾌감을 극대화하기 위해 공격 범위 전면 확대)
        if vars_obj.is_attacking:
            vars_obj.attack_timer -= 1
            
           # 콤보별 히트박스 영역 설계
            if vars_obj.combo_step in [1, 2]:
                # 1타, 2타: 대시하며 플레이어가 '지나간 자리(뒤쪽 궤적)'에 히트박스를 길게 배치
                attack_w = vars_obj.attack_range_width * 2.2   # 가로 크기 (~176px)
                attack_h = vars_obj.attack_range_height * 1.4  # 세로 크기 (~70px)
                
                if vars_obj.facing_right:
                    # 오른쪽으로 돌진했으므로, 현재 몸체 기준 '왼쪽(뒤쪽)'으로 히트박스 배치
                    ax = vars_obj.x + vars_obj.width - attack_w
                else:
                    # 왼쪽으로 돌진했으므로, 현재 몸체 기준 '오른쪽(뒤쪽)'으로 히트박스 배치
                    ax = vars_obj.x
                
                ay = vars_obj.y - 10
            else:
                # 3타: 광폭 피날레 충격파 범위 (제자리 폭발형이므로 몸 중심 전후방을 다 덮음)
                attack_w = vars_obj.attack_range_width * 3.5   # 초대형 (~280px)
                attack_h = vars_obj.attack_range_height * 2.2  # 세로 증가 (~110px)
                ax = vars_obj.x - (attack_w // 2) + (vars_obj.width // 2)
                ay = vars_obj.y + vars_obj.height - attack_h - 10

            vars_obj.attack_rect = pygame.Rect(ax, ay, attack_w, attack_h)

            # 실시간 피격 감지 루프
            if entities and not vars_obj.has_hit_enemy:
                for entity in entities:
                    if entity == self or getattr(entity, 'vars', None) == vars_obj:
                        continue
                    e_vars = getattr(entity, 'vars', None)
                    if not e_vars or getattr(e_vars, 'is_dead', False) or getattr(e_vars, 'is_hit', False):
                        continue

                    enemy_rect = pygame.Rect(e_vars.x, e_vars.y, e_vars.width, e_vars.height)
                    
                    if vars_obj.attack_rect.colliderect(enemy_rect):
                        vars_obj.has_hit_enemy = True
                        damage = getattr(vars_obj, 'attack_damage', 15)
                        attack_dir = 1 if vars_obj.facing_right else -1
                        
                        # 3타 시전 시에만 초강력 넉백(3.5배) 계수 적용, 1/2타는 단순 경직용(0.3배)
                        if vars_obj.combo_step == 3:
                            damage = int(damage * 1.5)
                            if hasattr(entity, 'take_damage'):
                                entity.take_damage(damage, knockback_dir=attack_dir * 0.3)
                        else:
                            if hasattr(entity, 'take_damage'):
                                entity.take_damage(damage, knockback_dir=attack_dir * 0.0)

            # 공격 모션 지속 프레임 종료 시 정산 루프
            if vars_obj.attack_timer <= 0:
                vars_obj.is_attacking = False
                vars_obj.attack_rect = None
                
                # 공용 변수인 vars_obj.attack_cooldown_timer를 직접 세팅하여 인풋 핸들러와 데이터 동기화
                if vars_obj.combo_step in [1, 2]:
                    vars_obj.attack_cooldown_timer = 0.15  # 1, 2타 후 조작 대기 쿨타임
                elif vars_obj.combo_step == 3:
                    vars_obj.attack_cooldown_timer = 0.25  # 3타 후 조작 대기 쿨타임
                
                # 콤보 초기화 및 만료 핸들러
                if vars_obj.combo_step == 3 or not vars_obj.has_hit_enemy:
                    vars_obj.combo_step = 0
        else:
            vars_obj.attack_rect = None