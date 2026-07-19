# ==========================================================================
# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드
# [SCAN_MODE] EXTRACTION_TARGET_PROJECT
# ==========================================================================
# 📄 [요청 1] TARGET: extraction_target_project/main.py (266-318라인)
# ----------------------------------------------------------
```python
def draw(self, screen, camera_offset=(0, 0)):
        """플레이어 본체 이미지와 공격 시 쇠파이프 콤보 이펙트를 화면에 렌더링합니다."""
        ox, oy = camera_offset
        # 🎬 1. 캐릭터 본체 스프라이트 시퀀스 추출 및 출력 (기존 순정 로직 완벽 보존)
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
        
        # ─────────────────────────────────────────────────────────────
        # 🎯 [새로운 시스템 추가] 쇠파이프 타격 범위(이펙트) 가시화 및 콤보별 연출
        # ─────────────────────────────────────────────────────────────
        if getattr(self.vars, 'is_attacking', False) and getattr(self.vars, 'attack_rect', None):
            # 카메라 좌표계가 반영된 실시간 이펙트 렌더링 사각형 변환
            eff_rect = pygame.Rect(
                self.vars.attack_rect.x - ox,
                self.vars.attack_rect.y - oy,
                self.vars.attack_rect.width,
                self.vars.attack_rect.height
            )
            
            # 투명도(Alpha) 표현이 가능한 이펙트 전용 특수 표면(Surface) 생성 (최적화 결합)
            effect_surf = pygame.Surface((eff_rect.width, eff_rect.height), pygame.SRCALPHA)
            
            # 현재 콤보 단수(1타, 2타, 3타막타)에 맞춰 시각 효과 가변 분기
            combo = getattr(self.vars, 'combo_step', 1)
            if combo == 1:
                # 1타: 신속하게 파고드는 블루 화이트 타격 잔상 (반투명)
                color = (52, 152, 219, 140) 
                pygame.draw.ellipse(effect_surf, color, (0, 0, eff_rect.width, eff_rect.height))
            elif combo == 2:
                # 2타: 좌우 반전 궤적으로 휘두르는 날카로운 옐로우 타격 잔상
                color = (241, 196, 15, 140)
                pygame.draw.ellipse(effect_surf, color, (0, 0, eff_rect.width, eff_rect.height))
            elif combo == 3:
                # 3타: 제자리 고정 묵직한 오렌지-레드 대형 광역 내려찍기 충격파 연출
                color = (231, 76, 60, 180)
                # 바닥 충격파 영역 생성
                pygame.draw.rect(effect_surf, color, (0, 0, eff_rect.width, eff_rect.height), border_radius=8)
                # 크래시 방지 및 시인성을 위한 내부 화이트 하이라이트 테두리 선 추가
                pygame.draw.rect(effect_surf, (255, 255, 255, 220), (0, 0, eff_rect.width, eff_rect.height), 3, border_radius=8)
                
            # 최종 연산 완료된 이펙트를 게임 화면에 블릿(Blit) 출력
            screen.blit(effect_surf, (eff_rect.x, eff_rect.y))
```

# 📄 [요청 2] TARGET: extraction_target_project/player/player_main.py (146-217라인)
# ----------------------------------------------------------
```python
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
```

# 📄 [요청 3] TARGET: extraction_target_project/enemy/enemys/test_enemy1/test_enemy1_main.py (197-247라인)
# ----------------------------------------------------------
```python
    def draw(self, screen, camera_offset=(0, 0)):
        if self.vars.is_dead:
            return # 죽었으면 렌더링 스킵 (추후 사망 시체 애니메이션 추가 공간)
            
        render_x = self.vars.x - camera_offset[0]
        render_y = self.vars.y - camera_offset[1]
        
        # 🎨 피격(is_hit) 시 빨간색 상자, 평소에는 주황색 상자로 렌더링하여 피격 피드백 제공!
        body_color = (231, 76, 60) if self.vars.is_hit else (241, 196, 15)
        
        rect = pygame.Rect(render_x, render_y, self.vars.width, self.vars.height)
        pygame.draw.rect(screen, body_color, rect)
        pygame.draw.rect(screen, (44, 62, 80), rect, 2)
        
        # 눈 렌더링
        eye_x = render_x + (self.vars.width - 12 if self.vars.direction == 1 else 6)
        pygame.draw.rect(screen, (0, 0, 0), (eye_x, render_y + 15, 6, 6))

    def draw_debug_overlay(self, screen, camera_offset=(0, 0)):
        """인공지능 적(TestEnemy1)의 AABB 경계상자 및 상태 머신 메타데이터를 화면에 투영합니다."""
        if not DEBUG or getattr(self.vars, 'is_dead', False) or not screen:
            return

        ox, oy = camera_offset
        e_width = getattr(self.vars, 'width', 0)
        e_height = getattr(self.vars, 'height', 0)

        # 1. 🔴 TestEnemy1 피격 판정 상자(AABB) 실선 렌더링
        if e_width > 0 and e_height > 0:
            aabb_rect = pygame.Rect(self.vars.x - ox, self.vars.y - oy, e_width, e_height)
            pygame.draw.rect(screen, (255, 0, 0), aabb_rect, 2)

        # 2. 📊 AI 상태 구조 및 물리 데이터 추적 (Lazy Evaluation)
        try:
            font = pygame.font.SysFont("Consolas", 12)
        except:
            font = pygame.font.Font(None, 12)

        debug_texts = [
            f"HP: {self.vars.hp}/{getattr(self.vars, 'max_hp', '??')}",
            f"STATE: {getattr(self, 'state', 'NONE')}",            # self 직속 속성 추적으로 변경
            f"VEL: ({getattr(self.vars, 'vx', 0):.1f}, {getattr(self.vars, 'vy', 0):.1f})",
            f"GND: {getattr(self, 'on_ground', False)}"             # 누락된 실시간 접지 데이터 바인딩
        ]

        for i, text in enumerate(debug_texts):
            text_surf = font.render(text, True, (255, 0, 0))
            screen.blit(text_surf, (self.vars.x - ox, self.vars.y - oy - 15 - (i * 13)))

        if DEBUG:
            print(f"[test_enemy1_main.py] draw_debug_overlay() -> Rendered AI Enemy AABB: HP={self.vars.hp}, STATE={getattr(self.vars, 'state', 'NONE')}")
```
