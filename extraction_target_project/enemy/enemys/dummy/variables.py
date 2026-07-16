class DummyVariables:
    def __init__(self, x, y):
        # 📐 위치 및 크기
        self.x = x
        self.y = y
        self.width = 50
        self.height = 70
        
        # 💫 실시간 중력 및 위치 피벗 동적 보정 변수
        self.vy = 0.0
        self.is_grounded = False
        
        # ❤️ 능력치 상태
        self.hp = 100
        self.max_hp = 100
        
        # 💫 피격(Hit) 관련 상태 변수
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 10
        
        # 🎯 맵 에디터 인스펙터 연동 가시성 변수 프로토콜 완벽 주입
        self.is_visible = True
        
        # 🧱 위치/피벗 자동 보정 베이스 라인
        self.initial_y_offset = self.height