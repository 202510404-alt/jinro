# player/motions/ground_motions.py
from player.motions.motion_base import MotionBase

class GroundMotions(MotionBase):
    def handle_state(self, vars_obj):
        # 공중에 떠 있다면 지상 모션 판정을 하지 않음
        if vars_obj.is_jumping:
            return None
            
        if vars_obj.is_moving:
            return vars_obj.move_state  # "WALK" 또는 "RUN" 반환
        else:
            return "IDLE"