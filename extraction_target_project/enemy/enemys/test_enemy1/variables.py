# [📂 enemy/enemys/test_enemy1/variables.py]
import pygame

class TestEnemy1Variables:
    def __init__(self):
        # 1. 기본 식별 및 플래그
        self.is_enemy = True          # 💡 이전 단계에서 만든 하이브리드 최적화 가드를 위한 핵심 적 태그!
        self.hp = 100                 # 체력
        self.max_hp = 100             # 최대 체력
        self.is_dead = False          # 사망 여부
        self.is_hit = False           # 피격 경직 상태 여부
        self.hit_timer = 0            # 피격 경직 타이머
        
        # 2. 물리 및 기본 위치 데이터 (main에서 실시간으로 대입/업데이트되는 변수들)
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.width = 40
        self.height = 60
        
        # 3. AI 이동 및 속도 제어
        self.patrol_speed = 1.5       # 평소 순찰할 때 걷는 속도
        self.chase_speed = 3.2        # 플레이어를 발견하고 쫓아갈 때 뛰는 속도
        self.direction = 1            # 바라보는 방향 (1: 오른쪽, -1: 왼쪽)
        
        # 4. AI 인지 범위 및 추적 시스템 (픽셀 단위)
        self.detection_range = 350    # 플레이어를 감지하는 시야 범위
        self.attack_range = 45        # 근접 공격을 시작하는 무기 사정거리
        
        # 5. 어그로 시간(초/프레임) 관리
        self.lost_timer = 0           # 실시간 시야 상실 타이머
        self.lost_delay = 180         # 시야에서 벗어나도 3초(180프레임) 동안 추적을 유지
        
        # 6. 공격 동작 관리
        self.attack_cooldown = 0      # 다음 공격까지 남은 쿨타임
        self.attack_ready_time = 30   # 공격 모션 전 선딜레이 시간 (0.5초 = 30프레임)
        self.attack_total_cooldown = 60 # 공격 완료 후 재사용 대기 시간 (1초 = 60프레임)