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
import settings

DEBUG = False

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
            self.vars.attack_obb = None

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
            if getattr(self.vars, 'attack_mode', 'NORMAL') == 'NORMAL':
                if self.vars.is_moving:
                    # 현재 move_state("RUN" 또는 "WALK")에 맞는 속도를 가져옵니다.
                    target_speed = self.vars.run_speed if self.vars.move_state == "RUN" else self.vars.walk_speed
                    direction = 1 if self.vars.facing_right else -1
                    
                    # 💡 감속 비율을 0.4에서 0.7~0.8 정도로 올려주거나, 
                    # 아예 1.0으로 만들면 공격 중에도 대시 속도가 시원하게 유지됩니다!
                    vars_target_modifier = 0.75  # 75% 속도 유지 (원하는 대로 조절 가능)
                    target_vx = target_speed * direction * vars_target_modifier
                    
                    self.vars.vx += (target_vx - self.vars.vx) * min(1.0, 0.25 * fps_scale)
                else:
                    self.vars.vx *= max(0.0, 1.0 - (0.35 * fps_scale))
            else:
                # DASH 모드는 전투 프로세서 내부의 고유 가속도 프로파일 유지를 위해 관성 보존 패스 처리합니다.
                pass
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
        """플레이어 본체 이미지와 공격 시 콤보 이펙트 및 임시 돌진 범위 시각화를 화면에 렌더링합니다."""
# 파일 상단의 로컬 DEBUG 기본값과 전역 settings 스위치를 상호 결합하여 동기화
        global DEBUG
        current_debug_state = DEBUG or getattr(settings, 'DEBUG_SHOW_HITBOX', False)
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

        # 3. 🔴 [임시 이펙트] 돌진 공격(DASH) 범위 실시간 빨간색 렌더링
        if self.vars.is_attacking and getattr(self.vars, 'attack_mode', 'NORMAL') == 'DASH':
            attack_obb = getattr(self.vars, 'attack_obb', None)
            if attack_obb is not None:
                obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y = attack_obb
                
                # 수직 방향 벡터 계산
                perp_x = -dir_y
                perp_y = dir_x

                # 카메라도 함께 움직이므로 오프셋(ox, oy)을 빼서 실제 화면 좌표를 도출합니다.
                corners = [
                    (obb_cx + dir_x * half_len + perp_x * half_wid - ox, obb_cy + dir_y * half_len + perp_y * half_wid - oy),
                    (obb_cx - dir_x * half_len + perp_x * half_wid - ox, obb_cy - dir_y * half_len + perp_y * half_wid - oy),
                    (obb_cx - dir_x * half_len - perp_x * half_wid - ox, obb_cy - dir_y * half_len - perp_y * half_wid - oy),
                    (obb_cx + dir_x * half_len - perp_x * half_wid - ox, obb_cy + dir_y * half_len - perp_y * half_wid - oy)
                ]

                # 알파 채우기를 위한 독립 서피스 생성 및 알파 채널 블릿 연산
                overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                pygame.draw.polygon(overlay, (255, 0, 0, 75), corners)  # 내부 반투명 레드 가이드라인
                screen.blit(overlay, (0, 0))

                # 경계선 실선 그리기
                pygame.draw.polygon(screen, (255, 0, 0), corners, 2)  # 외곽 붉은색 경계선

                if DEBUG:
                    print(f"[player_main.py] draw() -> Rendered DASH OBB Area: center=({obb_cx}, {obb_cy}), len={half_len}, wid={half_wid}")

        # 4. 🟢 [디버그 오버레이] 플레이어 피격 판정 상자(AABB) 실시간 녹색 렌더링
        if DEBUG:
            # 플레이어의 width와 height 속성이 설정되어 있는지 안전 필터링 거침
            p_width = getattr(self.vars, 'width', 0)
            p_height = getattr(self.vars, 'height', 0)
            if p_width > 0 and p_height > 0:
                aabb_rect = pygame.Rect(self.vars.x - ox, self.vars.y - oy, p_width, p_height)
                pygame.draw.rect(screen, (0, 255, 0), aabb_rect, 2)
                
                # 런타임 성능 저하 방지를 위해 디버그 스위치 기반 정밀 로깅 수행
                print(f"[player_main.py] draw() -> Rendered Player AABB: rect=({aabb_rect.x}, {aabb_rect.y}, {aabb_rect.width}, {aabb_rect.height})")