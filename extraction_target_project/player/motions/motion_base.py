# player/motions/motion_base.py
class MotionBase:
    def __init__(self):
        pass
    
    def handle_state(self, vars_obj):
        """각 모션 클래스에서 플레이어 변수를 보고 상태를 판정할 메서드 (오버라이딩용)"""
        pass