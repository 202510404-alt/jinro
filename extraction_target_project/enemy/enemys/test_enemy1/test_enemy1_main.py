# [📂 enemy/enemys/test_enemy1/test_enemy1_main.py]
import pygame
import math
# 우리가 정의한 TestEnemy1Variables 설정을 안전하게 임포트합니다.
from enemy.enemys.test_enemy1.variables import TestEnemy1Variables

DEBUG = True

class TestEnemy1:
    def __init__(self, x, y):
        # 1. variables.py에 명시된 모든 변수를 실시간 데이터로 장착!
        self.vars = TestEnemy1Variables()
        self.vars.x = x
        self.vars.y = y
        
        # 2. 실시간 AI 상태 제어 변수
        self.state = "PATROL" # PATROL, CHASE, LOST, ATTACK
        
        # 물리 연산용 접지 플래그 (점프 판단 및 낙하 판정용)
        self.on_ground = False

    def take_damage(self, amount, knockback_dir=0):
        """플레이어의 공격을 받았을 때 데미지를 받고 넉백되는 피격 로직"""
        if self.vars.is_dead:
            return
            
        self.vars.hp = max(0, self.vars.hp - amount)
        self.vars.is_hit = True
        self.vars.hit_timer = 20  # 약 0.3초간 완벽 경직 및 넉백
        
        # 타격을 받으면 즉시 뒤로 튕겨 나감 (넉백 가속도 주입)
        if knockback_dir != 0:
            self.vars.vx = knockback_dir * 350.0  # 넉백 강도 설정
        
        # 맞자마자 플레이어를 향해 상태를 '추적(CHASE)' 모드로 강제 강제 전환
        self.state = "CHASE"
        
        print(f"💥 [TestEnemy1] 피격! 체력: {self.vars.hp}/{self.vars.max_hp}")
        
        if self.vars.hp <= 0:
            self.vars.is_dead = True
            self.vars.vx = 0
            print("💀 [TestEnemy1] 사망함.")

    def check_line_of_sight(self, player_obj, platforms):
        """적과 플레이어 사이에 벽(플랫폼)이 가로막고 있는지 선형 보간(LERP) 검사"""
        if not hasattr(player_obj, 'vars'):
            return False
            
        px, py = player_obj.vars.x, player_obj.vars.y
        ex, ey = self.vars.x, self.vars.y
        
        # 거리가 감지 범위보다 멀면 즉시 감지 실패
        distance = math.hypot(px - ex, py - ey)
        if distance > self.vars.detection_range:
            return False
            
        steps = int(distance / 10) + 1
        for i in range(steps):
            t = i / steps
            lx = ex + (px - ex) * t
            ly = ey + (py - ey) * t
            
            for plat in platforms:
                plat_x = getattr(plat, 'x', 0)
                plat_y = getattr(plat, 'y', 0)
                plat_w = getattr(plat, 'width', 0) or getattr(plat, 'w', 40)
                plat_h = getattr(plat, 'height', 0) or getattr(plat, 'h', 40)
                
                plat_rect = pygame.Rect(plat_x, plat_y, plat_w, plat_h)
                if plat_rect.collidepoint(lx, ly):
                    return False
                    
        return True

    def update_with_dt(self, player_obj, platforms, game_map, dt):
        """
        인게임 루프에서 매 프레임 호출하는 핵심 업데이트 메서드.
        피격 경직 중일 때는 AI 행동 패턴을 일시정지하고 물리 넉백 슬라이딩 감속만 처리합니다.
        """
        # dt 가드 설정
        dt = min(dt, 0.1)

        # ----------------- [1. 피격 경직(Hit State) 및 넉백 감쇠 연산] -----------------
        if self.vars.is_hit:
            self.vars.hit_timer -= 1
            if self.vars.hit_timer <= 0:
                self.vars.is_hit = False
                
            # 바닥 마찰력으로 넉백에 의한 속도를 서서히 미끄러지며 줄임
            self.vars.vx *= 0.85
            
            # 경직 상태에서도 벽 충돌 및 중력 처리는 유지
            self._apply_gravity_and_collisions(platforms, game_map, dt)
            return

        if self.vars.is_dead:
            self.vars.vx = 0
            self._apply_gravity_and_collisions(platforms, game_map, dt)
            return

        # ----------------- [2. AI 상태 머신 연산 및 속도(vx) 설정] -----------------
        can_see_player = self.check_line_of_sight(player_obj, platforms)
        dx = player_obj.vars.x - self.vars.x if hasattr(player_obj, 'vars') else 0
        distance_to_player = abs(dx)

        if self.state == "PATROL":
            self.vars.vx = self.vars.direction * self.vars.patrol_speed
            if can_see_player:
                self.state = "CHASE"

        elif self.state == "CHASE":
            if dx > 0:
                self.vars.direction = 1
            elif dx < 0:
                self.vars.direction = -1
            self.vars.vx = self.vars.direction * self.vars.chase_speed
            
            if distance_to_player <= self.vars.attack_range:
                self.state = "ATTACK"
                self.vars.attack_cooldown = 40
            elif not can_see_player:
                self.state = "LOST"
                self.vars.lost_timer = self.vars.lost_delay

        elif self.state == "LOST":
            self.vars.lost_timer -= 1
            if can_see_player:
                self.state = "CHASE"
                self.vars.lost_timer = 0
            elif self.vars.lost_timer <= 0:
                self.state = "PATROL"

        elif self.state == "ATTACK":
            self.vars.vx = 0
            self.vars.attack_cooldown -= 1
            if self.vars.attack_cooldown <= 0:
                if distance_to_player > self.vars.attack_range:
                    self.state = "CHASE"
                else:
                    self.vars.attack_cooldown = 40

        # AI 연산 후 최종 물리 및 플랫폼 충돌 적용
        self._apply_gravity_and_collisions(platforms, game_map, dt)

    def _apply_gravity_and_collisions(self, platforms, game_map, dt):
        """순수 중력 및 플랫폼 충돌 로직"""
        # 중력 적용
        GRAVITY = 980.0 * dt
        self.vars.vy += GRAVITY
        if self.vars.vy > 900.0:
            self.vars.vy = 900.0

        # X축 이동 및 충돌
        self.vars.x += self.vars.vx * dt * 60.0
        self_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)

        for plat in platforms:
            p_vars = getattr(plat, 'vars', None)
            plat_x = getattr(p_vars if p_vars else plat, 'x', 0)
            plat_y = getattr(p_vars if p_vars else plat, 'y', 0)
            plat_w = getattr(p_vars if p_vars else plat, 'width', 0) or getattr(plat, 'w', 40)
            plat_h = getattr(p_vars if p_vars else plat, 'height', 0) or getattr(plat, 'h', 40)
            plat_rect = pygame.Rect(plat_x, plat_y, plat_w, plat_h)
            
            if self_rect.colliderect(plat_rect):
                if self.vars.y + self.vars.height > plat_rect.top + 4 and self.vars.y < plat_rect.bottom - 4:
                    if self.vars.vx > 0:
                        self.vars.x = plat_rect.left - self.vars.width
                        self.vars.direction = -1
                    elif self.vars.vx < 0:
                        self.vars.x = plat_rect.right
                        self.vars.direction = 1
                    break

        # Y축 이동 및 충돌
        old_bottom = self.vars.y + self.vars.height
        self.vars.y += self.vars.vy * dt
        self_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)
        self.on_ground = False

        for plat in platforms:
            p_vars = getattr(plat, 'vars', None)
            plat_x = getattr(p_vars if p_vars else plat, 'x', 0)
            plat_y = getattr(p_vars if p_vars else plat, 'y', 0)
            plat_w = getattr(p_vars if p_vars else plat, 'width', 0) or getattr(plat, 'w', 40)
            plat_h = getattr(p_vars if p_vars else plat, 'height', 0) or getattr(plat, 'h', 40)
            plat_rect = pygame.Rect(plat_x, plat_y, plat_w, plat_h)
            
            if self_rect.colliderect(plat_rect):
                if self.vars.vy >= 0 and old_bottom <= plat_rect.top + 12:
                    self.vars.y = plat_rect.top - self.vars.height
                    self.vars.vy = 0
                    self.on_ground = True
                    break

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