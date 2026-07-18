# ==========================================================================
# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드
# [SCAN_MODE] EXTRACTION_TARGET_PROJECT
# ==========================================================================
# 📄 [요청 1] TARGET: extraction_target_project/player/combat_processor.py (1-167라인)
# ----------------------------------------------------------
```python
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
```

# 📄 [요청 2] TARGET: extraction_target_project/player/input_handler.py (1-67라인)
# ----------------------------------------------------------
```python
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
```

# 📄 [요청 3] TARGET: extraction_target_project/player/variables.py (1-85라인)
# ----------------------------------------------------------
```python
# player/variables.py
from settings import GROUND_Y

class PlayerVariables:
    def __init__(self, x, y):
        # 🧍 기본 물리 변수
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.walk_speed = 4
        self.run_speed = 8
        self.jump_power = 16
        self.gravity = 0.8
        self.vertical_velocity = 0
        self.is_jumping = False
        self.current_state = "IDLE"
        self.facing_right = True
        self.is_moving = False
        self.move_state = "WALK"
        
        # 🧍 물리 가속도 변수 보충 (가변 프레임 및 관성 마찰 연산의 축)
        self.vx = 0.0
        self.vy = 0.0
        
        # ⚔️ 공격 및 콤보 관련 변수
        self.is_attacking = False       # 현재 공격 애니메이션/모션이 재생 중인가?
        self.combo_step = 0             # 0: 공격안함, 1: 1타, 2: 2타, 3: 3타
        self.attack_timer = 0           # 공격 모션이 유지되는 프레임 수
        self.attack_duration = 15       # 공격 모션 1회당 유지 시간
        self.has_hit_enemy = False      # 이번 공격 타수에서 적을 맞췄는가?
        
        # ⚔️ 전투 확장성 확보 (v1.3 연동용 기본 공격 공격력)
        self.attack_damage = 15
        
        # ⏱️ 콤보 유효 타이머 (1.5초 = 90프레임)
        self.combo_expire_time = 90     
        self.combo_timer = 0            
        
        # 📐 공격 범위(히트박스) 크기 설정
        self.attack_range_width = 80
        self.attack_range_height = 50
        self.attack_rect = None         
        
        # player/variables.py 내부 __init__ 하단에 추가할 변수 프로토콜
        self.attack_cooldown_timer = 0.0  # 공격 입력 및 콤보 조작 제한 타이머 (초 단위)
        self.target_enemy = None          # 현재 콤보 사이클 내에서 정밀 조준 중인 적 객체 참조

        # 🎬 [애니메이션 핵심 제어 변수]
        self.anim_timer = 0             # 프레임 카운터
        self.anim_speed = 8             # 숫자가 낮을수록 애니메이션이 빨라짐 (8프레임마다 다음 장)
        self.current_frame_idx = 0      # 리스트에서 현재 몇 번째 이미지를 그릴지 인덱스
        
        # 🎬 콤보 애니메이션 제어 확장 (콤보 타수별 프레임 재생 딜레이 개별 설정)
        self.state_delays = {
            "IDLE": 8,
            "WALK": 6,
            "RUN": 4,
            "ATTACK": 5,
            "ATTACK_1": 5,
            "ATTACK_2": 5,
            "ATTACK_3": 5
        }
        
        # 🚀 점프 선딜레이 타이머 (W 누른 순간 5프레임 동안만 READY_JUMP 유지)
        self.ready_jump_timer = 0

        # ❤️ HP 및 생존 관련 변수
        self.max_hp = 100
        self.hp = 100
        self.is_dead = False

    def take_damage(self, amount):
        """데미지를 입어 hp를 감소시키고, 0 이하가 되면 사망 처리합니다."""
        if self.is_dead or amount <= 0:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.is_dead = True

    def heal(self, amount):
        """체력을 회복시키되, 최대 체력을초과하지 않도록 합니다."""
        if self.is_dead or amount <= 0:
            return
        self.hp = min(self.max_hp, self.hp + amount)
```

# 📄 [요청 4] TARGET: extraction_target_project/player/player_main.py (1-155라인)
# ----------------------------------------------------------
```python
# src/player/player_main.py
import pygame
from player.variables import PlayerVariables
from player.input_handler import PlayerInputHandler
from player.asset_loader import PlayerAssetLoader          # 🌟 절대경로 추적 로더 연동
from player.physics_processor import PlayerPhysicsProcessor # 🌟 물리 엔진 연동
from player.combat_processor import PlayerCombatProcessor   # 🌟 전투 엔진 연동
from player.motions.ground_motions import GroundMotions
from player.motions.air_motions import AirMotions
from player.motions.attack_motions import AttackMotions

class Player:
    def __init__(self, x, y):
        # 데이터 및 입력 핸들러 초기화
        self.vars = PlayerVariables(x, y)
        self.vars_obj = self.vars  # 하위 호환성 및 외부 접근 편의를 위해 vars_obj 연결
        self.input_handler = PlayerInputHandler()
        
        # 🌟 분리된 컴포넌트 조립 (경로 수정이 완료된 에셋 로더 가동)
        self.assets = PlayerAssetLoader(self.vars)
        self.physics_engine = PlayerPhysicsProcessor()
        self.combat_engine = PlayerCombatProcessor()
        
        # 애니메이션 모션 판독기들 조립
        self.ground_motion_processor = GroundMotions()
        self.air_motion_processor = AirMotions()
        self.attack_motion_processor = AttackMotions()

    def update_animation_state(self):
        """현재 플레이어 변수를 분석해 상태 문자열(애니메이션 키)을 결정합니다."""
        state = None
        if self.vars.is_attacking:
            state = self.attack_motion_processor.handle_state(self.vars)
        elif self.vars.is_jumping or self.vars.vertical_velocity != 0:
            state = self.air_motion_processor.handle_state(self.vars)
        else:
            state = self.ground_motion_processor.handle_state(self.vars)
            
        if state is not None:
            self.vars.current_state = state

    def update(self, platforms, entities=None, game_map=None, dt=1.0/60.0):
        """플레이어의 모든 입력, 이동, 충돌, 애니메이션 프레임을 실시간 업데이트합니다."""
        
        # 가변 프레임 환경에 대응하기 위한 프레임 스케일러 보정값 계산
        fps_scale = dt * 60.0

        # ⏱️ [누락 해결] 콤보 유효 타이머 감소 연산 (시간 경과 시 콤보 리셋 보장)
        if getattr(self.vars, 'combo_timer', 0) > 0:
            self.vars.combo_timer -= fps_scale
            if self.vars.combo_timer < 0:
                self.vars.combo_timer = 0

        # 💀 사망 상태(is_dead == True) 예외 처리 및 기초 동작 제한
        if self.vars.is_dead:
            self.vars.is_moving = False
            self.vars.is_attacking = False
            self.vars.attack_rect = None
            
            # 최소한의 물리 엔진(중력, 충돌 판정)만 처리하여 바닥에 떨어질 수 있게 함 (dt 반영)
            self.physics_engine.process(self.vars, platforms, game_map=game_map, dt=dt)
            
            # 사망 애니메이션 상태 적용 (DEAD 에셋이 없는 경우 기본 IDLE 대기 상태 유지)
            if "DEAD" in self.assets.images:
                self.vars.current_state = "DEAD"
            else:
                self.vars.current_state = "IDLE"
                
            # 애니메이션 프레임 업데이트 (fps_scale 반영)
            anim_list = self.assets.images.get(self.vars.current_state, [])
            if anim_list:
                self.vars.anim_timer += fps_scale
                delay = getattr(self.vars, 'state_delays', {}).get(self.vars.current_state, self.vars.anim_speed)
                if self.vars.anim_timer >= delay:
                    self.vars.anim_timer = 0
                    self.vars.current_frame_idx = (self.vars.current_frame_idx + 1) % len(anim_list)
            return

        # 1. ⌨️ 사용자 키보드 입력 분석 (인자 전달 구조 유지)
        keys = pygame.key.get_pressed()
        self.input_handler.update(self.vars, keys)

        # 🪐 [관성 물리 메커니즘 통합]
        if self.vars.is_attacking:
            # 공격(돌진) 중일 때는 입력에 의한 속도 제어를 우회하고, 자연스러운 감속(마찰력)만 적용
            self.vars.vx *= max(0.0, 1.0 - (0.35 * fps_scale))
            self.vars.vy *= max(0.0, 1.0 - (0.35 * fps_scale))
        else:
            if self.vars.is_moving:
                # 가속
                target_speed = self.vars.run_speed if self.vars.move_state == "RUN" else self.vars.walk_speed
                direction = 1 if self.vars.facing_right else -1
                target_vx = target_speed * direction
                # 가속률 적용하여 target_vx에 도달
                self.vars.vx += (target_vx - self.vars.vx) * min(1.0, 0.25 * fps_scale)
            else:
                # 감속
                self.vars.vx *= max(0.0, 1.0 - (0.35 * fps_scale))
            
            # 공격 중이 아닐 때는 vy도 자연스럽게 감속
            self.vars.vy *= max(0.0, 1.0 - (0.35 * fps_scale))

        # 최종 물리 좌표(x, y) 업데이트
        self.vars.x += self.vars.vx * fps_scale
        self.vars.y += self.vars.vy * fps_scale

        # 2. 🪐 [오류 수정] 분리된 엔진 컴포넌트 가동 (물리 및 전투 엔진 인터페이스 및 dt 결합 완벽 갱신)
        self.physics_engine.process(self.vars, platforms, game_map=game_map, dt=dt)
        self.combat_engine.process(self.vars, entities=entities, dt=dt)

        # 3. 🎬 상태 기반 애니메이션 프레임 제어
        self.update_animation_state()
        
        anim_list = self.assets.images.get(self.vars.current_state, [])
        if anim_list:
            # [가변 보정] 델타 프레임 가중치를 더해 어떤 프레임에서도 일정한 속도로 애니메이션 재생
            self.vars.anim_timer += fps_scale
            # 각 상태(State)별로 지정된 프레임 딜레이 적용 (없으면 기본 anim_speed인 8 적용)
            delay = getattr(self.vars, 'state_delays', {}).get(self.vars.current_state, self.vars.anim_speed)
            if self.vars.anim_timer >= delay:
                self.vars.anim_timer = 0
                self.vars.current_frame_idx = (self.vars.current_frame_idx + 1) % len(anim_list)

    def update_with_dt(self, platforms, game_map, dt, entities=None):
        """main.py의 호출 인터페이스를 지원하기 위한 update 래퍼 메서드"""
        self.update(platforms, entities=entities, game_map=game_map, dt=dt)

    def draw(self, screen, camera_offset=(0, 0)):
        """플레이어 본체 이미지와 공격 시 콤보 이펙트를 화면에 렌더링합니다."""
        ox, oy = camera_offset
        # 🎬 1. 캐릭터 본체 스프라이트 시퀀스 추출 및 출력
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
        
        # 2. ⚔️ 공격 애니메이션 중일 때 콤보 검기 이펙트 출력 (원본 로직 완벽 보존)
        if self.vars.is_attacking and self.vars.combo_step in self.assets.effect_images:
            effect_img = self.assets.effect_images[self.vars.combo_step]
            
            # 플레이어가 바라보는 방향에 맞춰 이펙트도 반전 및 위치 정렬
            if not self.vars.facing_right:
                effect_img = pygame.transform.flip(effect_img, True, False)
                screen.blit(effect_img, (self.vars.x - ox - 60, self.vars.y - oy))
            else:
                screen.blit(effect_img, (self.vars.x - ox + 30, self.vars.y - oy))
```

# 📄 [요청 5] TARGET: extraction_target_project/player/physics_processor.py (1-77라인)
# ----------------------------------------------------------
```python
# player/physics_processor.py
import pygame
from settings import SCREEN_WIDTH, GROUND_Y

class PlayerPhysicsProcessor:
    def __init__(self):
        pass

    def process(self, vars_obj, platforms, game_map=None, dt=1.0/60.0):
        # 1. Y축 좌표를 업데이트하기 전에 '이전 발끝 위치'를 먼저 기록
        old_bottom = vars_obj.y + vars_obj.height

        # 가변 프레임 환경(dt)에 맞춘 가속 스케일러 연산
        fps_scale = dt * 60.0

        # 중력 적용 및 Y축 좌표 실제 이동
        vars_obj.vertical_velocity += vars_obj.gravity * fps_scale
        vars_obj.y += vars_obj.vertical_velocity * fps_scale

        player_rect = pygame.Rect(vars_obj.x, vars_obj.y, vars_obj.width, vars_obj.height)
        on_sub_platform = False

        # 플랫폼 충돌 정밀 검사
        for platform in platforms:
            # [GHOST 분기] 통과형 플랫폼은 연산에서 제외
            if not platform.vars.is_solid:
                continue
                
            plat_rect = pygame.Rect(platform.vars.x, platform.vars.y, platform.vars.width, platform.vars.height)
            
            if player_rect.colliderect(plat_rect):
                # ─── A. 하강/낙하 중일 때 (착지 처리: SOLID & ONE_WAY 공통) ───
                if vars_obj.vertical_velocity > 0:
                    # [하드코딩 제거] 매직 넘버 12 대신 낙하 속도와 프레임 보정치를 연동한 동적 착지 임계값 산출
                    dynamic_threshold = max(12.0, vars_obj.vertical_velocity * fps_scale + 2.0)
                    
                    if old_bottom <= platform.vars.y + dynamic_threshold:
                        vars_obj.y = platform.vars.y - vars_obj.height
                        vars_obj.vertical_velocity = 0
                        vars_obj.is_jumping = False
                        on_sub_platform = True
                        
                        # 💡 [차후 기능 확장 가드] 플랫폼 객체에 특수 밟기 기믹(무너짐 등) 기능이 있다면 동적 호출
                        if hasattr(platform, "on_stepped"):
                            platform.on_stepped(vars_obj, dt)
                        break
                
                # ─── B. 점프 상승 중일 때 (천장 충돌 처리: ONLY SOLID) ───
                elif vars_obj.vertical_velocity < 0:
                    # 아래에서 위로 통과할 수 없는 플랫폼 유형인 경우에만 정수리를 막음
                    if not platform.vars.passable_from_bottom:
                        # 이전 프레임의 머리 꼭대기 위치를 가변 dt 스케일에 맞춰 정확하게 역산
                        old_top = vars_obj.y - (vars_obj.vertical_velocity * fps_scale)
                        if old_top >= platform.vars.y + platform.vars.height:
                            vars_obj.y = platform.vars.y + platform.vars.height
                            vars_obj.vertical_velocity = 0 
                            
                            # 💡 [차후 기능 확장 가드] 천장 충돌 시 플랫폼 특수 기믹(스위치 작동 등) 확장 인터페이스
                            if hasattr(platform, "on_head_bump"):
                                platform.on_head_bump(vars_obj, dt)

        # 맵 시스템의 메인 바닥 착지 처리
        if not on_sub_platform:
            g_y = game_map.ground_y if (game_map and hasattr(game_map, 'ground_y')) else GROUND_Y
            if vars_obj.y + vars_obj.height >= g_y:
                vars_obj.y = g_y - vars_obj.height
                vars_obj.vertical_velocity = 0
                vars_obj.is_jumping = False

        # 좌측 화면 경계 밖 이탈 제어
        if vars_obj.x < 0:
            vars_obj.x = 0

        # 우측 화면/월드 경계 밖 이탈 제어 (유동적 가변 맵 대응 너비 반영)
        max_width = game_map.width if game_map else SCREEN_WIDTH
        if vars_obj.x > max_width - vars_obj.width:
            vars_obj.x = max_width - vars_obj.width
```

# 📄 [요청 6] TARGET: extraction_target_project/player/motions/attack_motions.py (1-14라인)
# ----------------------------------------------------------
```python
# player/motions/attack_motions.py
from player.motions.motion_base import MotionBase

class AttackMotions(MotionBase):
    def handle_state(self, vars_obj):
        # 플레이어가 공격 중일 때만 작동
        if vars_obj.is_attacking:
            if vars_obj.combo_step == 1:
                return "ATTACK_1"
            elif vars_obj.combo_step == 2:
                return "ATTACK_2"
            elif vars_obj.combo_step == 3:
                return "ATTACK_3"
        return None
```

# 📄 [요청 7] TARGET: extraction_target_project/player/motions/motion_base.py (1-8라인)
# ----------------------------------------------------------
```python
# player/motions/motion_base.py
class MotionBase:
    def __init__(self):
        pass
    
    def handle_state(self, vars_obj):
        """각 모션 클래스에서 플레이어 변수를 보고 상태를 판정할 메서드 (오버라이딩용)"""
        pass
```

# 📄 [요청 8] TARGET: extraction_target_project/player/asset_loader.py (12-60라인)
# ----------------------------------------------------------
```python
    def load_all_assets(self, vars_obj):
        # 🌟 현재 파일(src/player/asset_loader.py) 위치 기준 상위의 src/ 폴더 절대 경로 추출
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 정확히 src/assets/images/player 경로 조립
        base_dir = os.path.join(src_dir, "assets", "images", "player")
        move_dir = os.path.join(base_dir, "player_move")
        effect_dir = os.path.join(base_dir, "attack_effect")
        
        try:
            # 🎬 1. 캐릭터 모션 이미지 로드 (여러 장의 프레임을 리스트로 바인딩)
            self.images = {
                # 대기: 1 -> 2 -> 3
                "IDLE": self._load_series(move_dir, ["player_stand1.png", "player_stand2.png", "player_stand3.png"], vars_obj.width, vars_obj.height),
                
                # 이동/달리기: 1 -> 2 -> 3 (동일한 3장 애니메이션 시퀀스 공유)
                "WALK": self._load_series(move_dir, ["player_run1.png", "player_run2.png", "player_run3.png"], vars_obj.width, vars_obj.height),
                "RUN": self._load_series(move_dir, ["player_run1.png", "player_run2.png", "player_run3.png"], vars_obj.width, vars_obj.height),
                
                # 점프 시작 찰나 (W 누른 순간)
                "READY_JUMP": self._load_series(move_dir, ["player_readyjump.png"], vars_obj.width, vars_obj.height),
                
                # 공중 체공 전체 (상승/하강 전체 루프): 1 -> 2 -> 3
                "JUMP_UP": self._load_series(move_dir, ["player_jump1.png", "player_jump2.png", "player_jump3.png"], vars_obj.width, vars_obj.height),
                "FALL": self._load_series(move_dir, ["player_jump1.png", "player_jump2.png", "player_jump3.png"], vars_obj.width, vars_obj.height),
                
                # ⚔️ 기존 공격 모션 (애니메이션 연동 전까지 첫 번째 프레임으로 안전 유지)
                "ATTACK_1": self._load_series(move_dir, ["player_stand1.png"], vars_obj.width, vars_obj.height),
                "ATTACK_2": self._load_series(move_dir, ["player_stand1.png"], vars_obj.width, vars_obj.height),
                "ATTACK_3": self._load_series(move_dir, ["player_stand1.png"], vars_obj.width, vars_obj.height)
            }

            # 🧱 2. 공격 콤보 이펙트 이미지 로드
            self.effect_images = {
                1: pygame.image.load(os.path.join(effect_dir, "effect_hit1.png")).convert_alpha(),
                2: pygame.image.load(os.path.join(effect_dir, "effect_hit2.png")).convert_alpha(),
                3: pygame.image.load(os.path.join(effect_dir, "effect_hit3.png")).convert_alpha()
            }
            # 원본과 완벽히 동일하게 이펙트 규격 자동화 (플레이어 너비의 2배 스케일링)
            for step in self.effect_images:
                self.effect_images[step] = pygame.transform.scale(
                    self.effect_images[step], (vars_obj.width * 2, vars_obj.height)
                )

        except pygame.error as e:
            print(f"\n❌ 에러: 플레이어 또는 이펙트 에셋 로드 실패! ({e})")
            print(f"참조 실패한 디렉터리: {base_dir}")
            pygame.quit()
            sys.exit()
```

# 📄 [요청 9] TARGET: extraction_target_project/enemy/enemys/dummy/dummy_main.py (58-65라인)
# ----------------------------------------------------------
```python

    def check_player_attack(self, player_obj):
        """플레이어의 실시간 공격 히트박스 충돌 감지"""
        # 🎯 [구조 보환] 플레이어가 없거나(에디터 모드), 플레이어가 공격 상태가 아니면 안전하게 패스
        if not player_obj or not hasattr(player_obj, 'vars') or not player_obj.vars.is_attacking or not player_obj.vars.attack_rect:
            return

        dummy_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)
```

# 📄 [요청 10] TARGET: extraction_target_project/settings.py (1-70라인)
# ----------------------------------------------------------
```python
# src/settings.py

# 🖥️ 1. 내 모니터에 실제로 뜰 안전한 창 크기 (기기 화면 밖으로 안 삐져나감)
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# 🎮 2. 게임 내부에서 연산할 거대한 가상 크기 (이 숫자가 클수록 화면이 축소되어 캐릭터가 작아 보임!)
# 가로 세로 비율을 실제 창 크기(4:3) 비율과 비슷하게 맞추면 화면이 찌그러지지 않고 예쁩니다.
VIRTUAL_WIDTH = 1600
VIRTUAL_HEIGHT = 1200

FPS = 60

# 🌟 땅바닥의 높이는 이제 뻥튀기 된 가상 화면 높이(1200) 기준으로 자동 조절됩니다.
GROUND_Y = VIRTUAL_HEIGHT - 120

SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)

# ============================================================
# 🎥 Camera Tuning (Elastic / Dynamic Smoothing)
# ------------------------------------------------------------
# - CAMERA_SMOOTHING (0~1):
#   60FPS에서 "한 프레임에 목표로 얼마나 따라갈지"를 의미합니다.
#   값이 낮을수록 무겁고 느긋(카메라가 늦게 따라옴), 높을수록 즉각 반응합니다.
CAMERA_SMOOTHING = 0.12
CAMERA_DEADZONE_W = 180
CAMERA_DEADZONE_H = 120

# - 순간 낙하/텔레포트에서 카메라가 너무 빠르게 휘지 않게 상한을 걸고 싶으면 숫자를 넣으세요.
#   (None이면 제한 없음)
CAMERA_MAX_SPEED_PX_PER_SEC = None

# ============================================================
# 🗺️ Map / Ground Rendering Padding (카메라 잘림 방지)
# ------------------------------------------------------------
# 가상 월드 좌표(VIRTUAL_* 기준)에서 바닥 타일이 끊겨 보이는 것을 막기 위해
# 좌우로 여유분을 추가로 그립니다.
#
# 핵심:
# - 카메라가 오른쪽 끝(map_width 근처)으로 이동할 때, 화면 우측까지 꽉 차게 보이려면
#   최소한 viewport_w/2 만큼은 추가로 타일이 존재해야 합니다.
# - 여기에 "Alpha Padding" 성격의 여유값을 더해 시각적 끊김을 완전히 제거합니다.
MAP_PADDING_EXTRA_X = 200
MAP_PADDING_X = (VIRTUAL_WIDTH / 2.0) + float(MAP_PADDING_EXTRA_X)

# ============================================================
# 🌄 2단 패럴랙스 배경 시스템 (backdrop + background)
# ------------------------------------------------------------
# [구조 설명]
#   - backdrop  (전역 원경): 하늘 통짜 이미지. Y 완전 고정, X만 아주 느리게 스크롤.
#   - background (지상 배경): 지면(ground_y) 기준으로 고정된 이미지. X만 중간 속도로 타일링.
#
# [비율(RATIO) 의미]
#   - 0.0 : 카메라가 움직여도 배경이 전혀 안 움직임(완전 고정)
#   - 0.5 : 카메라 이동의 50%만 따라옴(원근감/깊이감)
#   - 1.0 : 월드와 동일하게 움직임(패럴랙스 효과 없음)

# 전역 원경(backdrop) X축 속도 비율
# - 값이 작을수록 배경이 거의 안 움직여서 멀리 있는 느낌을 줍니다.
BACKDROP_X_RATIO = 0.05

# 지상 배경(background) X축 속도 비율
# - 지면 바로 뒤의 배경이므로 backdrop보다 빠르게 따라와야 원근감이 생깁니다.
BACKGROUND_X_RATIO = 0.35

# 🧱 X축 타일링 빈틈 방지 여유분 (픽셀 단위)
# - 카메라 이동 시 타일 경계면에서 1픽셀 빈틈이 생기는 현상을 막기 위한 좌우 안전 여백.
# - Y축 무한 타일링은 이 시스템에서 사용하지 않으므로 X 패딩만 남깁니다.
BG_TILE_PADDING_X = 100
```
