# ==========================================================================
# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드
# [SCAN_MODE] EXTRACTION_TARGET_PROJECT
# ==========================================================================
# 📄 [요청 1] TARGET: extraction_target_project/player/player_main.py (1-60라인)
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

    def update(self, platforms, game_map=None):
        """플레이어의 모든 입력, 이동, 충돌, 애니메이션 프레임을 실시간 업데이트합니다."""
        # 💀 사망 상태(is_dead == True) 예외 처리 및 기초 동작 제한
        if self.vars.is_dead:
            self.vars.is_moving = False
            self.vars.is_attacking = False
            self.vars.attack_rect = None
            
            # 최소한의 물리 엔진(중력, 충돌 판정)만 처리하여 바닥에 떨어질 수 있게 함
            self.physics_engine.process(self.vars, platforms, game_map=game_map)
            
            # 사망 애니메이션 상태 적용 (DEAD 에셋이 없는 경우 기본 IDLE 대기 상태 유지)
            if "DEAD" in self.assets.images:
                self.vars.current_state = "DEAD"
            else:
                self.vars.current_state = "IDLE"
                
            # 애니메이션 프레임 업데이트
            anim_list = self.assets.images.get(self.vars.current_state, [])
```

# 📄 [요청 2] TARGET: extraction_target_project/player/physics_processor.py (5-61라인)
# ----------------------------------------------------------
```python
class PlayerPhysicsProcessor:
    def process(self, vars_obj, platforms, game_map=None):
        # 1. Y축 좌표를 업데이트하기 전에 '이전 발끝 위치'를 먼저 기록해둡니다.
        old_bottom = vars_obj.y + vars_obj.height

        # 중력 적용 및 실제 Y축 이동
        vars_obj.vertical_velocity += vars_obj.gravity
        vars_obj.y += vars_obj.vertical_velocity

        player_rect = pygame.Rect(vars_obj.x, vars_obj.y, vars_obj.width, vars_obj.height)
        on_sub_platform = False

        # 플랫폼 충돌 검사
        for platform in platforms:
            # [GHOST 분기] 통과형 플랫폼은 물리 판정을 아예 건너뜁니다.
            if not platform.vars.is_solid:
                continue
                
            plat_rect = pygame.Rect(platform.vars.x, platform.vars.y, platform.vars.width, platform.vars.height)
            
            if player_rect.colliderect(plat_rect):
                # ─── A. 떨어지는 중일 때 (착지 처리: SOLID & ONE_WAY 공통) ───
                if vars_obj.vertical_velocity > 0:
                    # 이동하기 전 발끝(old_bottom)이 플랫폼 윗면보다 높게 있었을 때만 착지시킵니다.
                    if old_bottom <= platform.vars.y + 10:
                        vars_obj.y = platform.vars.y - vars_obj.height
                        vars_obj.vertical_velocity = 0
                        vars_obj.is_jumping = False
                        on_sub_platform = True
                        break
                
                # ─── B. 점프하며 올라가는 중일 때 (머리 충돌 처리: ONLY SOLID) ───
                elif vars_obj.vertical_velocity < 0:
                    # 아래에서 위로 통과 불가능한(SOLID) 플랫폼인 경우만 머리를 막습니다.
                    if not platform.vars.passable_from_bottom:
                        # 이동하기 전 정수리가 플랫폼 아랫면보다 아래에 있었는지 검증
                        old_top = vars_obj.y - vars_obj.vertical_velocity
                        if old_top >= platform.vars.y + platform.vars.height:
                            vars_obj.y = platform.vars.y + platform.vars.height
                            vars_obj.vertical_velocity = 0 # 상승 속도 리셋 (뚝 떨어지게 만듦)

        # 메인 바닥 착지 검사
        if not on_sub_platform:
            g_y = game_map.ground_y if (game_map and hasattr(game_map, 'ground_y')) else GROUND_Y
            if vars_obj.y + vars_obj.height >= g_y:
                vars_obj.y = g_y - vars_obj.height
                vars_obj.vertical_velocity = 0
                vars_obj.is_jumping = False

        # 좌측 맵 바운더리 제한
        if vars_obj.x < 0:
            vars_obj.x = 0

        # 우측 맵 바운더리 제한
        max_width = game_map.width if game_map else SCREEN_WIDTH
        if vars_obj.x > max_width - vars_obj.width:
            vars_obj.x = max_width - vars_obj.width
```

# 📄 [요청 3] TARGET: extraction_target_project/enemy/enemys/dummy/dummy_main.py (76-91라인)
# ----------------------------------------------------------
```python
    def update(self, player_obj, platforms, game_map=None):
        """인게임 실시간 피격 판정과 함께, 플레이어와 동일한 규칙의 물리 업데이트 처리"""
        if self.vars.hp <= 0:
            return
        
        # 1. 플레이어 피격 체크
        self.check_player_attack(player_obj)

        # 2. 플레이어의 PhysicsProcessor와 완벽히 동일한 메커니즘으로 중력 및 지형 착지 연동
        self.apply_gravity_and_physics(platforms, game_map)

        # 3. 피격 경직 타이머
        if self.vars.is_hit:
            self.vars.hit_timer -= 1
            if self.vars.hit_timer <= 0:
                self.vars.is_hit = False
```
