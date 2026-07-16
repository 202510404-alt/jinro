# src/platform_system/variables.py
from platform_system.platform_settings import * # 🌟 src. 제거하여 경로 인식 해결

class PlatformVariables:
    def __init__(self, x, y, 
                 width=DEFAULT_PLATFORM_WIDTH, 
                 height=DEFAULT_PLATFORM_HEIGHT, 
                 is_solid=DEFAULT_IS_SOLID, 
                 is_visible=DEFAULT_IS_VISIBLE, 
                 passable_from_bottom=DEFAULT_PASSABLE_FROM_BOTTOM, 
                 platform_type="SOLID",  # SOLID, ONE_WAY, GHOST 기본값 세팅
                 **kwargs):
        """
        플랫폼의 속성들을 관리하는 데이터 클래스 (무결성 및 확장 규칙 준수)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_visible = is_visible                 
        
        # 가변 인자 매핑 유연성 확보
        if "platform_type" in kwargs:
            self.platform_type = kwargs["platform_type"]
        else:
            self.platform_type = platform_type

        # 플랫폼 타입 기반 판정 규칙 바인딩
        if self.platform_type == "SOLID":
            self.is_solid = True
            self.passable_from_bottom = False
        elif self.platform_type == "ONE_WAY":
            self.is_solid = True
            self.passable_from_bottom = True  # 하단 및 측면 통과 판정 활성화
        elif self.platform_type == "GHOST":
            self.is_solid = False
            self.passable_from_bottom = True  # 완전 전방향 통과 판정
            
        self.velocity_x = DEFAULT_PLATFORM_SPEED_X
        self.velocity_y = DEFAULT_PLATFORM_SPEED_Y