# player/motions/attack_motions.py
from player.motions.motion_base import MotionBase

class AttackMotions(MotionBase):
    def handle_state(self, vars_obj):
        # 플레이어가 공격 중일 때만 작동
        if vars_obj.is_attacking:
            if vars_obj.combo_step == 1:
                return "ATTACK_1"
            elif vars_obj.combo_step == 2:
                return "ATTACK_2"
            elif vars_obj.combo_step == 3:
                return "ATTACK_3"
        return None