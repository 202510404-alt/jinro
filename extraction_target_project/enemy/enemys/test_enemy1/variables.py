import pygame

class TestEnemy1Variables:
    def __init__(self, x, y):
        # 기본 물리 및 위치 데이터
        self.rect = pygame.Rect(x, y, 40, 60) # 임의 크기 설정
        self.vx = 0
        self.vy = 0
        self.speed = 2 # 플레이어 추적 시 속도
        
        # 상태 변수
        self.state = "IDLE" # IDLE, CHASE, ATTACK
        self.direction = 1  # 1: 우측, -1: 좌측
        
        # 🎯 감지 및 범위 설정 (핵심 로직용)
        self.detection_range = 300  # 플레이어 감지 범위 (픽셀)
        self.attack_range = 50     # 근접 공격 범위 (픽셀)
        
        # 애니메이션 및 쿨다운 (필요시)
        self.attack_cooldown = 0
        self.max_attack_cooldown = 60 # 프레임 단위 또는 타이머