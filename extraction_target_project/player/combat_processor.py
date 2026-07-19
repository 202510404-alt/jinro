# player/combat_processor.py
import math
import pygame

# 2.2. 정밀 디버깅 전용 파일 단위 로컬 스위치 배치
DEBUG = True


def _obb_vs_aabb_collide(cx, cy, half_len, half_wid, dir_x, dir_y, ax, ay, aw, ah):
    """
    돌진 궤적 기반 OBB(중심 cx,cy / 장축 half_len / 단축 half_wid / 방향 dir_x,dir_y)와
    적 히트박스 AABB(ax,ay,aw,ah) 간의 SAT(분리축 정리) 충돌 판정.
    """
    a_half_w = aw * 0.5
    a_half_h = ah * 0.5
    a_cx = ax + a_half_w
    a_cy = ay + a_half_h

    tx = a_cx - cx
    ty = a_cy - cy

    perp_x = -dir_y
    perp_y = dir_x

    # [축 1] OBB 장축
    proj_len = tx * dir_x + ty * dir_y
    r_aabb_on_dir = a_half_w * abs(dir_x) + a_half_h * abs(dir_y)
    if abs(proj_len) > half_len + r_aabb_on_dir:
        return False

    # [축 2] OBB 단축
    proj_wid = tx * perp_x + ty * perp_y
    r_aabb_on_perp = a_half_w * abs(perp_x) + a_half_h * abs(perp_y)
    if abs(proj_wid) > half_wid + r_aabb_on_perp:
        return False

    # [축 3] 월드 X축
    r_obb_on_x = half_len * abs(dir_x) + half_wid * abs(perp_x)
    if abs(tx) > a_half_w + r_obb_on_x:
        return False

    # [축 4] 월드 Y축
    r_obb_on_y = half_len * abs(dir_y) + half_wid * abs(perp_y)
    if abs(ty) > a_half_h + r_obb_on_y:
        return False

    return True


class PlayerCombatProcessor:
    def __init__(self):
        pass

    def process(self, vars_obj, entities=None, dt=0.0):
        # 가변 프레임 환경에 대응하기 위한 프레임 스케일러 보정값 계산
        fps_scale = dt * 60.0

        # 안전장치: 변수 객체에 쿨타임 필드가 없을 경우 동적 확보
        if not hasattr(vars_obj, 'attack_cooldown_timer'):
            vars_obj.attack_cooldown_timer = 0.0

        # 1. 공격 불가(쿨타임) 실시간 감쇄 연산
        if vars_obj.attack_cooldown_timer > 0.0:
            vars_obj.attack_cooldown_timer -= dt
            if vars_obj.attack_cooldown_timer < 0.0:
                vars_obj.attack_cooldown_timer = 0.0

# 2. 새로운 공격 모션 프레임 개시 시점 (트리거)
        if vars_obj.is_attacking and getattr(vars_obj, 'attack_timer', 0) == 0:
            if not hasattr(vars_obj, 'attack_mode'):
                vars_obj.attack_mode = "NORMAL"

            # 디버그용 Before 상태 백업
            if DEBUG:
                before_mode = vars_obj.attack_mode
                before_x = getattr(vars_obj, 'x', 0)
                before_y = getattr(vars_obj, 'y', 0)

            # 📐 [OBB 축 A점] 돌진/공격 개시 원점 박제
            vars_obj.attack_start_x = vars_obj.x
            vars_obj.attack_start_y = vars_obj.y
            vars_obj.has_hit_enemy = False

            # 타겟팅 공통 변수 상위 스코프 초기화
            target_enemy = None
            max_target_distance = vars_obj.attack_range_width * 2.0
            min_dist_sq = max_target_distance * max_target_distance

            # -------------------------------------------------------------
            # [A 트랙] 좌클릭 일반 제자리 콤보 공격 초기화
            # -------------------------------------------------------------
            if vars_obj.attack_mode == "NORMAL":
                if not hasattr(vars_obj, 'combo_step') or vars_obj.combo_step == 0:
                    vars_obj.combo_step = 1
                
                # 타수별 프레임 차등 제어
                vars_obj.attack_timer = 12 if vars_obj.combo_step in [1, 2] else 18
                vars_obj.target_enemy = None

            # -------------------------------------------------------------
            # [B 트랙] 우클릭 신규 대쉬 공격 초기화
            # -------------------------------------------------------------
            elif vars_obj.attack_mode == "DASH":
                vars_obj.attack_timer = 12
                dash_speed = 20.0

                # 🎯 대쉬 트랙 내 독립 레이더 가동 (공격 범위 2배 탐색)
                target_enemy = None
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

                # 대쉬 물리 구동 벡터 계산
                if target_enemy:
                    te_vars = target_enemy.vars
                    dx = te_vars.x - vars_obj.x
                    dy = te_vars.y - vars_obj.y
                    dist_sq = dx * dx + dy * dy
                    dist = math.sqrt(dist_sq) if dist_sq > 0 else 1.0

                    vars_obj.facing_right = (dx > 0)
                    y_margin = 25

                    if abs(dy) > y_margin:
                        vars_obj.vx = (dx / dist) * dash_speed
                        vars_obj.vy = (dy / dist) * dash_speed
                    else:
                        vars_obj.vx = dash_speed if vars_obj.facing_right else -dash_speed
                        vars_obj.vy = 0.0
                else:
                    vars_obj.vx = dash_speed if vars_obj.facing_right else -dash_speed
                    vars_obj.vy = 0.0

            # 규격화된 Before-After 디버그 로그 출력 (Lazy Evaluation)
            if DEBUG:
                print(f"[combat_processor.py] process() -> Attack Initialization Changed: Mode={before_mode} -> {vars_obj.attack_mode}, Origin=({before_x}, {before_y}) -> ({vars_obj.attack_start_x}, {vars_obj.attack_start_y}), Timer={vars_obj.attack_timer}")
                print(f"[combat_processor.py] process() -> Attack Initialized: mode={vars_obj.attack_mode}, step={getattr(vars_obj, 'combo_step', 0)}, target={vars_obj.target_enemy}")
        # -------------------------------------------------------------
        # 3. 공격 액션 진행 및 실시간 히트박스 / 피격 판정 루프 (완벽 복원)
        # -------------------------------------------------------------
        if vars_obj.is_attacking:
            # 원본 정수형 타이머 시스템에 맞추어 1프레임씩 감쇄 일관성 유지
            vars_obj.attack_timer -= 1

            # 🛠️ [멈춤 현상 완전 해결 핵심 핵심 영역] 
            # 공격 판정 프레임 후반부(마지막 4프레임) 혹은 후딜레이 진입 직전 상태인 경우,
            # 애니메이션 컨텍스트 유지를 위해 `is_attacking = True` 상태는 그대로 가두어 두되,
            # 사용자의 이동 키 입력 여부에 맞춰 물리 속도 벡터(`vx`)를 사전 개방하여 경직을 파쇄합니다.
            if vars_obj.attack_mode == "NORMAL" and vars_obj.attack_timer <= 4:
                if getattr(vars_obj, 'is_moving', False):
                    target_speed = vars_obj.run_speed if vars_obj.move_state == "RUN" else vars_obj.walk_speed
                    direction = 1 if vars_obj.facing_right else -1
                    vars_obj.vx = target_speed * direction

            # 3-1. 공격 모드 및 콤보 스텝별 히트박스 갱신 생성
            if vars_obj.attack_mode == "DASH":
                # 대쉬 공격은 무조건 이동 궤적 기반 OBB 판정 영역 사용
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
                    dir_x = 1.0 if vars_obj.facing_right else -1.0
                    dir_y = 0.0

                half_len = (seg_len * 0.5) + (vars_obj.attack_range_width * 0.5) + 80
                half_wid = (vars_obj.attack_range_height * 0.5) * 1.5
                obb_cx = (start_cx + cur_cx) * 0.5
                obb_cy = (start_cy + cur_cy) * 0.5

                vars_obj.attack_obb = (obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y)
                vars_obj.attack_rect = pygame.Rect(
                    int(obb_cx - half_len), int(obb_cy - half_wid),
                    int(half_len * 2), int(half_wid * 2)
                )

            elif vars_obj.attack_mode == "NORMAL":
                if vars_obj.combo_step in [1, 2]:
                    # 제자리 일반 공격 1, 2타: 플레이어 중심 기준 전방 지향 OBB 정적 구성
                    dir_x = 1.0 if vars_obj.facing_right else -1.0
                    dir_y = 0.0
                    half_len = vars_obj.attack_range_width * 0.5
                    half_wid = vars_obj.attack_range_height * 0.5
                    
                    # 시선 방향으로 판정 중심 약간 오프셋
                    obb_cx = (vars_obj.x + vars_obj.width * 0.5) + (dir_x * half_len * 0.5)
                    obb_cy = vars_obj.y + vars_obj.height * 0.5

                    vars_obj.attack_obb = (obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y)
                    vars_obj.attack_rect = pygame.Rect(
                        int(obb_cx - half_len), int(obb_cy - half_wid),
                        int(half_len * 2), int(half_wid * 2)
                    )
                else:
                    # 제자리 일반 공격 3타: 몸 중심 기준 확장 사양 고정 AABB 범위 공격
                    attack_w = vars_obj.attack_range_width * 1.6
                    attack_h = vars_obj.attack_range_height * 1.6
                    ax = vars_obj.x - (attack_w - vars_obj.width) * 0.5
                    ay = vars_obj.y - (attack_h - vars_obj.height) * 0.5

                    vars_obj.attack_obb = None
                    vars_obj.attack_rect = pygame.Rect(int(ax), int(ay), int(attack_w), int(attack_h))

            # 3-2. 실시간 피격 감지 및 대미지 인가 세션
            if entities and not vars_obj.has_hit_enemy:
                for entity in entities:
                    if entity is self or getattr(entity, 'vars', None) is vars_obj:
                        continue
                    e_vars = getattr(entity, 'vars', None)
                    if not e_vars or getattr(e_vars, 'is_dead', False) or getattr(e_vars, 'is_hit', False):
                        continue

                    # 충돌 기하 연산 분기
                    if vars_obj.attack_obb is not None:
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

                        # 대미지 및 넉백 계수 판정 처리
                        if vars_obj.attack_mode == "NORMAL" and vars_obj.combo_step == 3:
                            damage = int(damage * 1.5)
                            if hasattr(entity, 'take_damage'):
                                entity.take_damage(damage, knockback_dir=attack_dir * 0.0)
                        else:
                            if hasattr(entity, 'take_damage'):
                                entity.take_damage(damage, knockback_dir=attack_dir * 0.0)

                        if DEBUG:
                            print(f"[combat_processor.py] process() -> Hit Registered: Target={entity}, Damage={damage}")
                        break

            # 3-3. 공격 모션 시간 종료 시 상태 자원 정산 및 데이터 동기화
            if vars_obj.attack_timer <= 0:
                vars_obj.attack_timer = 0
                vars_obj.is_attacking = False
                vars_obj.attack_rect = None
                vars_obj.attack_obb = None

                # 트랙별 재사용 대기시간 독립 주입
                if vars_obj.attack_mode == "NORMAL":
                    if vars_obj.combo_step in [1, 2]:
                        vars_obj.attack_cooldown_timer = 0.15
                    elif vars_obj.combo_step == 3:
                        vars_obj.attack_cooldown_timer = 0.25

                    # 일반 공격 후속 연계 판정 정산 (적을 맞추지 못했거나 마지막 타수인 경우 콤보 리셋)
                    if vars_obj.combo_step == 3 or not vars_obj.has_hit_enemy:
                        vars_obj.combo_step = 0
                        vars_obj.combo_timer = 0
                else:
                    # DASH 모드는 고정 후딜레이 부여 후 연계 콤보 스텝 초기화 가드
                    vars_obj.attack_cooldown_timer = 0.2
                    vars_obj.combo_step = 0
                    vars_obj.combo_timer = 0
        else:
            vars_obj.attack_rect = None
            vars_obj.attack_obb = None