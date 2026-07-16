import pygame
import math
from .variables import TestEnemy1Variables

class TestEnemy1:
    def __init__(self, x, y):
        self.vars = TestEnemy1Variables(x, y)

    def update(self, player, platforms, game_map=None):
        # 1. 플레이어와의 거리 및 방향 계산
        dx = player.vars.rect.centerx - self.vars.rect.centerx
        dy = player.vars.rect.centery - self.vars.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        # 2. 플레이어가 있는 방향 설정
        if dx > 0:
            self.vars.direction = 1
        elif dx < 0:
            self.vars.direction = -1

        # 3. 거리 기반 상태 전이 알고리즘
        if distance <= self.vars.attack_range:
            # 공격 범위 안으로 들어오면 멈춰서 공격
            self.vars.state = "ATTACK"
            self.vars.vx = 0
            self.perform_attack(player)
        elif distance <= self.vars.detection_range:
            # 감지 범위 내에 있으면 추적
            self.vars.state = "CHASE"
            self.vars.vx = self.vars.direction * self.vars.speed
        else:
            # 범위 밖이면 대기
            self.vars.state = "IDLE"
            self.vars.vx = 0

        # 4. 물리 이동 및 충돌 처리
        self.vars.rect.x += self.vars.vx
        # (필요 시 기존 dummy 처럼 플랫폼/바닥 충돌 처리 구현 적용)

        # 5. 공격 쿨다운 차감
        if self.vars.attack_cooldown > 0:
            self.vars.attack_cooldown -= 1

    def perform_attack(self, player):
        if self.vars.attack_cooldown == 0:
            # 💥 플레이어에게 데미지 전달 인터페이스 호출
            if hasattr(player.vars, 'take_damage'):
                player.vars.take_damage(10) # 예시 데미지
            self.vars.attack_cooldown = self.vars.max_attack_cooldown

    def draw(self, screen, camera=None):
        # 카메라 오프셋 적용
        offset_x = camera.offset_x if camera else 0
        offset_y = camera.offset_y if camera else 0
        draw_rect = self.vars.rect.move(-offset_x, -offset_y)

        # 상태별 가시적 구분을 위해 색상 변경 (디버깅/테스트용)
        color = (0, 255, 0) # 기본 초록색 (IDLE)
        if self.vars.state == "CHASE":
            color = (255, 165, 0) # 추적 중 오렌지색
        elif self.vars.state == "ATTACK":
            color = (255, 0, 0) # 공격 중 빨간색

        pygame.draw.rect(screen, color, draw_rect)