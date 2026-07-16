# src/player/variables.py
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
        
        # ⚔️ 공격 및 콤보 관련 변수
        self.is_attacking = False       # 현재 공격 애니메이션/모션이 재생 중인가?
        self.combo_step = 0             # 0: 공격안함, 1: 1타, 2: 2타, 3: 3타
        self.attack_timer = 0           # 공격 모션이 유지되는 프레임 수
        self.attack_duration = 15       # 공격 모션 1회당 유지 시간
        self.has_hit_enemy = False      # 이번 공격 타수에서 적을 맞췄는가?
        
        # ⏱️ 콤보 유효 타이머 (1.5초 = 90프레임)
        self.combo_expire_time = 90     
        self.combo_timer = 0            
        
        # 📐 공격 범위(히트박스) 크기 설정
        self.attack_range_width = 80
        self.attack_range_height = 50
        self.attack_rect = None         
        
        # 🎬 [애니메이션 핵심 제어 변수]
        self.anim_timer = 0             # 프레임 카운터
        self.anim_speed = 8             # 숫자가 낮을수록 애니메이션이 빨라짐 (8프레임마다 다음 장)
        self.current_frame_idx = 0      # 리스트에서 현재 몇 번째 이미지를 그릴지 인덱스
        
        self.state_delays = {
            "IDLE": 8,
            "WALK": 6,
            "RUN": 4,
            "ATTACK": 5
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
        """체력을 회복시키되, 최대 체력을 초과하지 않도록 합니다."""
        if self.is_dead or amount <= 0:
            return
        self.hp = min(self.max_hp, self.hp + amount)