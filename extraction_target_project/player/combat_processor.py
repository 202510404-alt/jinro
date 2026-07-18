# [📂 player/combat_processor.py]
import pygame
import math


def _obb_vs_aabb_collide(cx, cy, half_len, half_wid, dir_x, dir_y, ax, ay, aw, ah):
    """
    돌진 궤적 기반 OBB(중심 cx,cy / 장축 half_len / 단축 half_wid / 방향 dir_x,dir_y)와
    적 히트박스 AABB(ax,ay,aw,ah) 간의 SAT(분리축 정리) 충돌 판정.
    필요한 분리축은 OBB의 두 축(dir, perp)과 AABB의 두 축(world X, world Y)뿐이며,
    전부 스칼라 연산으로 처리되어 프레임당 객체 생성이 발생하지 않아 GC 부하가 없다.
    """
    # 적 AABB의 중심 및 반경(half extent) 계산
    a_half_w = aw * 0.5
    a_half_h = ah * 0.5
    a_cx = ax + a_half_w
    a_cy = ay + a_half_h

    # 두 중심 사이 벡터
    tx = a_cx - cx
    ty = a_cy - cy

    # OBB 수직축(장축에 대한 법선) 계산
    perp_x = -dir_y
    perp_y = dir_x

    # [축 1] OBB 장축(dir) 위로 투영하여 겹침 검사
    proj_len = tx * dir_x + ty * dir_y
    r_aabb_on_dir = a_half_w * abs(dir_x) + a_half_h * abs(dir_y)
    if abs(proj_len) > half_len + r_aabb_on_dir:
        return False

    # [축 2] OBB 단축(perp) 위로 투영하여 겹침 검사
    proj_wid = tx * perp_x + ty * perp_y
    r_aabb_on_perp = a_half_w * abs(perp_x) + a_half_h * abs(perp_y)
    if abs(proj_wid) > half_wid + r_aabb_on_perp:
        return False

    # [축 3] 월드 X축 위로 투영하여 겹침 검사
    r_obb_on_x = half_len * abs(dir_x) + half_wid * abs(perp_x)
    if abs(tx) > a_half_w + r_obb_on_x:
        return False

    # [축 4] 월드 Y축 위로 투영하여 겹침 검사
    r_obb_on_y = half_len * abs(dir_y) + half_wid * abs(perp_y)
    if abs(ty) > a_half_h + r_obb_on_y:
        return False

    # 4개 분리축 전부에서 겹침이 확인되었으므로 충돌 확정
    return True


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

            # 📐 [OBB 축 A점] 돌진이 시작되는 현재 좌표를 궤적선의 시작점으로 기록
            vars_obj.attack_start_x = vars_obj.x
            vars_obj.attack_start_y = vars_obj.y

            # 🎯 [타겟팅] 좌클릭(is_targeting=True)일 때만 자동 타겟팅 수행, 우클릭은 비타겟팅 고정
            target_enemy = None
            if getattr(vars_obj, 'is_targeting', False):
                # 좌클릭 자동 타겟팅 사거리: 공격 판정 폭의 2배 거리 (스펙 규격 준수)
                max_target_distance = vars_obj.attack_range_width * 2.0
                min_dist_sq = max_target_distance * max_target_distance

                if entities:
                    for entity in entities:
                        if entity is self or getattr(entity, 'vars', None) is vars_obj:
                            continue
                        e_vars = getattr(entity, 'vars', None)
                        if not e_vars or getattr(e_vars, 'is_dead', False):
                            continue

                        dx = e_vars.x - vars_obj.x
                        dy = e_vars.y - vars_obj.y
                        dist_sq = dx * dx + dy * dy

                        if dist_sq <= min_dist_sq:
                            min_dist_sq = dist_sq
                            target_enemy = entity

            vars_obj.target_enemy = target_enemy

            # 3. 콤보 분기 및 돌진 속도 적용
            dash_speed = 75.0
            vars_obj.attack_timer = 12 if vars_obj.combo_step in [1, 2] else 18

            if vars_obj.combo_step in [1, 2]:
                # [1타/2타 공통] 돌진 방향 결정 로직
                if target_enemy:
                    te_vars = target_enemy.vars
                    dx = te_vars.x - vars_obj.x
                    dy = te_vars.y - vars_obj.y
                    dist_sq = dx * dx + dy * dy
                    dist = math.sqrt(dist_sq) if dist_sq > 0 else 1.0

                    vars_obj.facing_right = (dx > 0)
                    y_margin = 25

                    if abs(dy) > y_margin:
                        # Y축 미중첩: 적을 직접 향해 대각선으로 돌진
                        vars_obj.vx = (dx / dist) * dash_speed
                        vars_obj.vy = (dy / dist) * dash_speed
                    else:
                        # Y축 중첩: 가로 일직선으로 돌진
                        vars_obj.vx = dash_speed if dx > 0 else -dash_speed
                        vars_obj.vy = 0.0
                else:
                    # 비타겟팅(우클릭 또는 타겟 없음): 바라보는 방향으로 가로 돌진
                    vars_obj.vx = dash_speed if vars_obj.facing_right else -dash_speed
                    vars_obj.vy = 0.0

            elif vars_obj.combo_step == 3:
                # [3타] 제자리 오버랩 범위 공격
                vars_obj.vx = 0.0
                vars_obj.vy = 0.0

            vars_obj.has_hit_enemy = False

        # 4. 공격 액션 진행 중
        if vars_obj.is_attacking:
            vars_obj.attack_timer -= 1

            if vars_obj.combo_step in [1, 2]:
                # 📐 [OBB 계산] 시작점(A)과 현재점(B)을 잇는 궤적선을 축으로 회전된 판정 영역 생성
                start_x = getattr(vars_obj, 'attack_start_x', vars_obj.x)
                start_y = getattr(vars_obj, 'attack_start_y', vars_obj.y)

                start_cx = start_x + vars_obj.width * 0.5
                start_cy = start_y + vars_obj.height * 0.5
                cur_cx = vars_obj.x + vars_obj.width * 0.5
                cur_cy = vars_obj.y + vars_obj.height * 0.5

                seg_dx = cur_cx - start_cx
                seg_dy = cur_cy - start_cy
                seg_len = math.sqrt(seg_dx * seg_dx + seg_dy * seg_dy)

                if seg_len > 0.0001:
                    dir_x = seg_dx / seg_len
                    dir_y = seg_dy / seg_len
                else:
                    # 이동량이 거의 없는 프레임(대시 시작 직후 등)은 바라보는 방향을 축으로 대체
                    dir_x = 1.0 if vars_obj.facing_right else -1.0
                    dir_y = 0.0

                # 장축 절반 길이 = 이동 거리 절반 + 판정 폭 절반(칼날 길이 보정)
                half_len = (seg_len * 0.5) + (vars_obj.attack_range_width * 0.5)
                half_wid = vars_obj.attack_range_height * 0.5
                obb_cx = (start_cx + cur_cx) * 0.5
                obb_cy = (start_cy + cur_cy) * 0.5

                # 실제 판정에 쓰이는 OBB 파라미터 (튜플 1개만 재사용, GC 부하 최소화)
                vars_obj.attack_obb = (obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y)

                # 디버그 표시/기존 인터페이스 호환용 AABB 근사 사각형 (실제 판정에는 미사용)
                vars_obj.attack_rect = pygame.Rect(
                    int(obb_cx - half_len), int(obb_cy - half_wid),
                    int(half_len * 2), int(half_wid * 2)
                )
            else:
                # 3타: 제자리 오버랩 범위 (몸 중심 기준 확장된 AABB)
                attack_w = vars_obj.attack_range_width * 1.6
                attack_h = vars_obj.attack_range_height * 1.6
                ax = vars_obj.x - (attack_w - vars_obj.width) * 0.5
                ay = vars_obj.y - (attack_h - vars_obj.height) * 0.5

                vars_obj.attack_obb = None
                vars_obj.attack_rect = pygame.Rect(int(ax), int(ay), int(attack_w), int(attack_h))

            # 실시간 피격 감지 루프
            if entities and not vars_obj.has_hit_enemy:
                for entity in entities:
                    if entity is self or getattr(entity, 'vars', None) is vars_obj:
                        continue
                    e_vars = getattr(entity, 'vars', None)
                    if not e_vars or getattr(e_vars, 'is_dead', False) or getattr(e_vars, 'is_hit', False):
                        continue

                    if vars_obj.combo_step in [1, 2]:
                        obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y = vars_obj.attack_obb
                        hit = _obb_vs_aabb_collide(
                            obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y,
                            e_vars.x, e_vars.y, e_vars.width, e_vars.height
                        )
                    else:
                        enemy_rect = pygame.Rect(e_vars.x, e_vars.y, e_vars.width, e_vars.height)
                        hit = vars_obj.attack_rect.colliderect(enemy_rect)

                    if hit:
                        vars_obj.has_hit_enemy = True
                        damage = getattr(vars_obj, 'attack_damage', 15)
                        attack_dir = 1 if vars_obj.facing_right else -1

                        if vars_obj.combo_step == 3:
                            # 3타 시전 시에만 소형 넉백 효과 부여 (스펙 규격 준수)
                            damage = int(damage * 1.5)
                            if hasattr(entity, 'take_damage'):
                                entity.take_damage(damage, knockback_dir=attack_dir * 0.3)
                        else:
                            if hasattr(entity, 'take_damage'):
                                entity.take_damage(damage, knockback_dir=attack_dir * 0.0)

                        # 한 프레임 내 콜리전 갱신 플래그 중복 계산 방지: 적중 확정 즉시 루프 종료
                        break

            # 공격 모션 지속 프레임 종료 시 정산 루프
            if vars_obj.attack_timer <= 0:
                vars_obj.is_attacking = False
                vars_obj.attack_rect = None
                vars_obj.attack_obb = None

                # 공용 변수인 vars_obj.attack_cooldown_timer를 직접 세팅하여 인풋 핸들러와 데이터 동기화
                if vars_obj.combo_step in [1, 2]:
                    vars_obj.attack_cooldown_timer = 0.15  # 1, 2타 후 조작 대기 쿨타임
                elif vars_obj.combo_step == 3:
                    vars_obj.attack_cooldown_timer = 0.25  # 3타 후 조작 대기 쿨타임

                # ⚔️ [OnHit 전용 콤보 전환] 이번 타수가 적중하지 못했거나 3타가 끝났다면 콤보 완전 초기화.
                # 다음 클릭 시 input_handler.trigger_attack()이 combo_step==0을 보고 1타부터 재시작하도록 강제한다.
                if vars_obj.combo_step == 3 or not vars_obj.has_hit_enemy:
                    vars_obj.combo_step = 0
                    vars_obj.combo_timer = 0
        else:
            vars_obj.attack_rect = None
            vars_obj.attack_obb = None
