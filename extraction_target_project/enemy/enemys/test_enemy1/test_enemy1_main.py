# [📂 enemy/enemys/test_enemy1/test_enemy1_main.py]
import pygame
import math
# 우리가 정의한 TestEnemy1Variables 설정을 안전하게 임포트합니다.
from enemy.enemys.test_enemy1.variables import TestEnemy1Variables

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

    def check_line_of_sight(self, player_obj, platforms):
        """적과 플레이어 사이에 벽(플랫폼)이 가로막고 있는지 선형 보간(LERP) 검사"""
        if not hasattr(player_obj, 'vars'):
            return False
            
        px, py = player_obj.vars.x, player_obj.vars.y
        ex, ey = self.vars.x, self.vars.y
        
        # 거리가 감지 범위보다 멀면 즉시 감지 실패 (variables의 설정 참조)
        distance = math.hypot(px - ex, py - ey)
        if distance > self.vars.detection_range:
            return False
            
        # 레이캐스팅 정밀 해상도 (몇 단계로 나누어 선을 그어볼 것인가)
        steps = int(distance / 10) + 1
        for i in range(steps):
            t = i / steps
            # 적과 플레이어 사이의 보간 좌표 계산
            lx = ex + (px - ex) * t
            ly = ey + (py - ey) * t
            
            # 보간 좌표가 어떤 플랫폼 내부를 관통하는지 검사
            for plat in platforms:
                plat_x = getattr(plat, 'x', 0)
                plat_y = getattr(plat, 'y', 0)
                plat_w = getattr(plat, 'width', 0) or getattr(plat, 'w', 40)
                plat_h = getattr(plat, 'height', 0) or getattr(plat, 'h', 40)
                
                plat_rect = pygame.Rect(plat_x, plat_y, plat_w, plat_h)
                if plat_rect.collidepoint(lx, ly):
                    return False # 벽에 가로막혀 볼 수 없음!
                    
        return True # 가로막는 벽이 없으므로 플레이어 감지 성공!

    def update_with_dt(self, player_obj, platforms, game_map, dt):
        """
        인게임 루프에서 매 프레임 호출하는 핵심 업데이트 메서드.
        하드코딩된 바닥값 없이, 100% 맵에 배치된 platforms(지형) 위에서만 딛고 서도록 작동합니다.
        """
        # dt 가드 설정 (비정상적인 큰 변화 방지)
        dt = min(dt, 0.1)

        # ----------------- [1. AI 상태 머신 연산 및 속도(vx) 설정] -----------------
        can_see_player = self.check_line_of_sight(player_obj, platforms)
        
        # 플레이어와의 X축 거리 계산
        dx = player_obj.vars.x - self.vars.x if hasattr(player_obj, 'vars') else 0
        distance_to_player = abs(dx)

        # 상태 전환 처리
        if self.state == "PATROL":
            # 평화롭게 순찰 속도(patrol_speed)로 이동
            self.vars.vx = self.vars.direction * self.vars.patrol_speed
            
            # 플레이어가 시야에 들어왔을 때 즉시 어그로(CHASE) 상태 전환
            if can_see_player:
                self.state = "CHASE"
                print("🚨 적 발견! 추적 상태로 돌입합니다.")

        elif self.state == "CHASE":
            # 시야에 보인다면 방향을 계속 갱신하며 추격 속도로 쫓아감
            if dx > 0:
                self.vars.direction = 1
            elif dx < 0:
                self.vars.direction = -1
                
            self.vars.vx = self.vars.direction * self.vars.chase_speed
            
            # 플레이어가 사정거리 안으로 들어왔다면 멈춰 서서 공격 상태 전환
            if distance_to_player <= self.vars.attack_range:
                self.state = "ATTACK"
                self.vars.attack_cooldown = 40 # 딜레이 충전
            # 플레이어를 시야에서 놓쳤다면 경계(LOST) 상태로 전환
            elif not can_see_player:
                self.state = "LOST"
                self.vars.lost_timer = self.vars.lost_delay # 어그로 유지 타이머 작동 시작

        elif self.state == "LOST":
            self.vars.lost_timer -= 1
            if can_see_player:
                self.state = "CHASE"
                self.vars.lost_timer = 0
            elif self.vars.lost_timer <= 0:
                self.state = "PATROL"
                print("💤 어그로 해제. 순찰 복귀.")

        elif self.state == "ATTACK":
            self.vars.vx = 0
            self.vars.attack_cooldown -= 1
            if self.vars.attack_cooldown <= 0:
                # 공격 후 다시 플레이어 거리를 보고 상태 결정
                if distance_to_player > self.vars.attack_range:
                    self.state = "CHASE"
                else:
                    self.vars.attack_cooldown = 40

        # ----------------- [2. 중력 및 낙하 속도 처리 (Y축 가속)] -----------------
        GRAVITY = 980.0 * dt  # 픽셀 물리 기반 중력 가속도 계산
        self.vars.vy += GRAVITY
        if self.vars.vy > 900.0:  # 최대 종단 속도 제한
            self.vars.vy = 900.0

        # ----------------- [3. X축 이동 및 충돌 해결] -----------------
        self.vars.x += self.vars.vx * dt * 60.0
        self_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)

        for plat in platforms:
            p_vars = getattr(plat, 'vars', None)
            if p_vars:
                plat_x = getattr(p_vars, 'x', 0)
                plat_y = getattr(p_vars, 'y', 0)
                plat_w = getattr(p_vars, 'width', 0)
                plat_h = getattr(p_vars, 'height', 0)
            else:
                plat_x = getattr(plat, 'x', 0)
                plat_y = getattr(plat, 'y', 0)
                plat_w = getattr(plat, 'width', 0) or getattr(plat, 'w', 40)
                plat_h = getattr(plat, 'height', 0) or getattr(plat, 'h', 40)

            plat_rect = pygame.Rect(plat_x, plat_y, plat_w, plat_h)
            
            # 옆면 충돌 시 방향 전환 및 밀어내기
            if self_rect.colliderect(plat_rect):
                # 머리/발끝이 겹친 게 아닌 옆면 충돌일 경우에만 작동
                if self.vars.y + self.vars.height > plat_rect.top + 4 and self.vars.y < plat_rect.bottom - 4:
                    if self.vars.vx > 0:
                        self.vars.x = plat_rect.left - self.vars.width
                        self.vars.direction = -1  # 벽에 닿았으므로 반대방향 순찰
                    elif self.vars.vx < 0:
                        self.vars.x = plat_rect.right
                        self.vars.direction = 1   # 반대방향 순찰
                    break

        # ----------------- [4. Y축 이동 및 충돌 해결 (공중부양 차단 핵심)] -----------------
        # 수직 이동 전에 이전 발끝(Bottom) 좌표 백업
        old_bottom = self.vars.y + self.vars.height
        
        # Y축 이동분 반영
        self.vars.y += self.vars.vy * dt
        self_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)
        self.on_ground = False  # 접지 상태 초기화

        # 하드코딩(536)을 지우고, 배치되어 있는 모든 플랫폼들과의 충돌을 루프로 판정합니다.
        for plat in platforms:
            p_vars = getattr(plat, 'vars', None)
            if p_vars:
                plat_x = getattr(p_vars, 'x', 0)
                plat_y = getattr(p_vars, 'y', 0)
                plat_w = getattr(p_vars, 'width', 0)
                plat_h = getattr(p_vars, 'height', 0)
            else:
                plat_x = getattr(plat, 'x', 0)
                plat_y = getattr(plat, 'y', 0)
                plat_w = getattr(plat, 'width', 0) or getattr(plat, 'w', 40)
                plat_h = getattr(plat, 'height', 0) or getattr(plat, 'h', 40)

            plat_rect = pygame.Rect(plat_x, plat_y, plat_w, plat_h)
            
            # 발밑 충돌 체크 (위에서 아래로 떨어지는 도중 발끝이 플랫폼 윗면에 닿았는가?)
            if self_rect.colliderect(plat_rect):
                if self.vars.vy >= 0 and old_bottom <= plat_rect.top + 12:
                    self.vars.y = plat_rect.top - self.vars.height
                    self.vars.vy = 0
                    self.on_ground = True
                    break

    def draw(self, screen, camera_offset=(0, 0)):
        """적이 카메라 뷰포트에 연동되어 올바른 좌표에 렌더링되도록 처리"""
        render_x = self.vars.x - camera_offset[0]
        render_y = self.vars.y - camera_offset[1]
        
        # 주황색 몸통 상자 + 테두리 + 검은색 눈 렌더링 (투명 방지!)
        rect = pygame.Rect(render_x, render_y, self.vars.width, self.vars.height)
        pygame.draw.rect(screen, (241, 196, 15), rect)        # 주황색 몸체
        pygame.draw.rect(screen, (44, 62, 80), rect, 2)       # 테두리
        
        # 바라보는 방향(direction)에 따라 시선 포커싱 눈동자 그리기
        eye_x = render_x + (self.vars.width - 12 if self.vars.direction == 1 else 6)
        pygame.draw.rect(screen, (0, 0, 0), (eye_x, render_y + 15, 6, 6)) # 눈