# player/motions/air_motions.py
from player.motions.motion_base import MotionBase

class AirMotions(MotionBase):
    def handle_state(self, vars_obj):
        # 공중에 떠 있을 때만 판정
        if vars_obj.is_jumping:
            if vars_obj.vertical_velocity < 0:
                return "JUMP_UP"
            else:
                return "FALL"
        return None