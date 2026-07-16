# player/combat_processor.py
import pygame

class PlayerCombatProcessor:
    def process(self, vars_obj):
        if vars_obj.is_attacking:
            vars_obj.attack_timer -= 1
            
            # 공격 방향에 따라 히트박스 x좌표 산출
            if vars_obj.facing_right:
                attack_x = vars_obj.x + vars_obj.width
            else:
                attack_x = vars_obj.x - vars_obj.attack_range_width
                
            attack_y = vars_obj.y + (vars_obj.height // 4)
            
            vars_obj.attack_rect = pygame.Rect(
                attack_x, attack_y, 
                vars_obj.attack_range_width, vars_obj.attack_range_height
            )

            # 공격 종료 판정
            if vars_obj.attack_timer <= 0:
                vars_obj.is_attacking = False
                vars_obj.attack_rect = None
                
                # 적 타격 실패 시 콤보 리셋
                if not vars_obj.has_hit_enemy:
                    vars_obj.combo_step = 0
        else:
            vars_obj.attack_rect = None