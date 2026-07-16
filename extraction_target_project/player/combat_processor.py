# [📂 player/combat_processor.py]
import pygame
import math

class PlayerCombatProcessor:
    def __init__(self):
        self.attack_cooldown_timer = 0.0

    def process(self, vars_obj, entities=None, dt=0.0):
        # 1. 공격 딜레이(쿨타임) 연산
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt
            if self.attack_cooldown_timer > 0:
                return

        # 2. 새로운 공격 개시 시점 (is_attacking은 켜졌으나 타이머가 0일 때)
        if vars_obj.is_attacking and getattr(vars_obj, 'attack_timer', 0) == 0:
            if not hasattr(vars_obj, 'combo_step') or vars_obj.combo_step == 0:
                vars_obj.combo_step = 1

            # 🎯 [최적화 자동 타겟팅] 가장 가까운 유효 적 탐색
            target_enemy = None
            max_target_distance = vars_obj.attack_range_width * 1.5
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

            # 3. 콤보 분기 처리
            dash_speed = 750.0 # 시원한 돌진 속도감 부여
            
            if vars_obj.combo_step in [1, 2]:
                self.attack_cooldown_timer = 0.2 # 1, 2타 딜레이 0.2초
                vars_obj.attack_timer = 12       # 공격 판정 지속 프레임
                
                if target_enemy:
                    te_vars = target_enemy.vars
                    dx = te_vars.x - vars_obj.x
                    dy = te_vars.y - vars_obj.y
                    vars_obj.facing_right = (dx > 0)
                    
                    y_margin = 25 # 겹침 판정 픽셀 범주
                    if abs(dy) <= y_margin:
                        # 1) Y값 겹침 -> 수평 대시
                        vars_obj.vx = dash_speed if dx > 0 else -dash_speed
                        vars_obj.vy = 0
                    elif dy < -y_margin:
                        # 2) 적이 위 -> 대각선 위 돌진
                        vars_obj.vx = dash_speed * 0.7 if dx > 0 else -dash_speed * 0.7
                        vars_obj.vy = -dash_speed * 0.7
                    else:
                        # 3) 적이 아래 -> 대각선 아래 돌진
                        vars_obj.vx = dash_speed * 0.7 if dx > 0 else -dash_speed * 0.7
                        vars_obj.vy = dash_speed * 0.7
                else:
                    # 타겟이 없으면 바라보는 방향 수평 대시
                    vars_obj.vx = dash_speed if vars_obj.facing_right else -dash_speed
                    vars_obj.vy = 0
                    
            elif vars_obj.combo_step == 3:
                self.attack_cooldown_timer = 0.25 # 3타 막타 딜레이 0.25초
                vars_obj.attack_timer = 18
                
                # 💥 3타는 철저하게 돌진 없이 가만히 서서 밀치는 느낌!
                vars_obj.vx = 0
                # 점프 중 내려찍을 경우를 대비해 필요시 아래로 고정하거나 정지
                vars_obj.vy = 0 

            vars_obj.has_hit_enemy = False

        # 4. 공격 액션 진행 중 (히트박스 생성 및 타격 연산)
        if vars_obj.is_attacking:
            vars_obj.attack_timer -= 1
            
            # 요구사항: 공격 범위는 이펙트가 나오게 일치시켜야 함
            if vars_obj.combo_step in [1, 2]:
                attack_w = vars_obj.attack_range_width * 1.3
                attack_h = vars_obj.attack_range_height * 0.8
                ax = vars_obj.x + vars_obj.width if vars_obj.facing_right else vars_obj.x - attack_w
                ay = vars_obj.y + (vars_obj.height // 4)
            else:
                # 3타: 쇠파이프 내려찍기 광역 범위 (주변 폭발형 충격파)
                attack_w = vars_obj.attack_range_width * 2.0
                attack_h = vars_obj.attack_range_height * 1.5
                ax = vars_obj.x - (attack_w // 2) + (vars_obj.width // 2)
                ay = vars_obj.y + vars_obj.height - attack_h

            vars_obj.attack_rect = pygame.Rect(ax, ay, attack_w, attack_h)

            # 실시간 피격 판정 루프
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
                        
                        # 🎯 [넉백 조건 절대 제어] 3타만 강한 넉백 발동! 1,2타는 경직만
                        if vars_obj.combo_step == 3:
                            damage = int(damage * 1.5) # 3타 데미지 강화
                            if hasattr(entity, 'take_damage'):
                                entity.take_damage(damage, knockback_dir=attack_dir * 3.5)
                        else:
                            if hasattr(entity, 'take_damage'):
                                entity.take_damage(damage, knockback_dir=attack_dir * 0.3)

            # 공격 모션 프레임 만료 시 종료
            if vars_obj.attack_timer <= 0:
                vars_obj.is_attacking = False
                vars_obj.attack_rect = None
                
                if vars_obj.combo_step == 3 or not vars_obj.has_hit_enemy:
                    vars_obj.combo_step = 0
        else:
            vars_obj.attack_rect = None