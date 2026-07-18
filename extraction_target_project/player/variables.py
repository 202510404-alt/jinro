# player/variables.py
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

        # 🧍 물리 가속도 변수 보충 (가변 프레임 및 관성 마찰 연산의 축)
        self.vx = 0.0
        self.vy = 0.0

        # ⚔️ 공격 및 콤보 관련 변수
        self.is_attacking = False       # 현재 공격 애니메이션/모션이 재생 중인가?
        self.combo_step = 0             # 0: 공격안함, 1: 1타, 2: 2타, 3: 3타
        self.attack_timer = 0           # 공격 모션이 유지되는 프레임 수
        self.attack_duration = 15       # 공격 모션 1회당 유지 시간
        self.has_hit_enemy = False      # 이번 공격 타수에서 적을 맞췄는가?

        # ⚔️ 전투 확장성 확보 (v1.3 연동용 기본 공격력)
        self.attack_damage = 15

        # ⏱️ 콤보 유효 타이머 (1.5초 = 90프레임)
        self.combo_expire_time = 90
        self.combo_timer = 0

        # 📐 공격 범위(히트박스) 크기 설정
        self.attack_range_width = 80
        self.attack_range_height = 50
        self.attack_rect = None

        # player/variables.py 내부 __init__ 하단에 추가할 변수 프로토콜
        self.attack_cooldown_timer = 0.0  # 공격 입력 및 콤보 조작 제한 타이머 (초 단위)
        self.target_enemy = None          # 현재 콤보 사이클 내에서 정밀 조준 중인 적 객체 참조

        # 📐 [OBB 돌진 판정용 신규 변수]
        self.attack_start_x = x           # 현재 타수의 돌진이 시작된 X좌표 (OBB 축의 A점)
        self.attack_start_y = y           # 현재 타수의 돌진이 시작된 Y좌표 (OBB 축의 A점)
        self.attack_obb = None            # (중심x, 중심y, 장축절반, 단축절반, 방향x, 방향y) 튜플
        self.is_targeting = False         # True: 좌클릭발 자동 타겟팅, False: 우클릭발 비타겟팅 고정

        # 🎬 [애니메이션 핵심 제어 변수]
        self.anim_timer = 0             # 프레임 카운터
        self.anim_speed = 8             # 숫자가 낮을수록 애니메이션이 빨라짐 (8프레임마다 다음 장)
        self.current_frame_idx = 0      # 리스트에서 현재 몇 번째 이미지를 그릴지 인덱스

        # 🎬 콤보 애니메이션 제어 확장 (콤보 타수별 프레임 재생 딜레이 개별 설정)
        self.state_delays = {
            "IDLE": 8,
            "WALK": 6,
            "RUN": 4,
            "ATTACK": 5,
            "ATTACK_1": 5,
            "ATTACK_2": 5,
            "ATTACK_3": 5
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
        """체력을 회복시키되, 최대 체력을초과하지 않도록 합니다."""
        if self.is_dead or amount <= 0:
            return
        self.hp = min(self.max_hp, self.hp + amount)
