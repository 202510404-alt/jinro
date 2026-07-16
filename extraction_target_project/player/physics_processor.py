# src/player/physics_processor.py
import pygame
from settings import SCREEN_WIDTH, GROUND_Y

class PlayerPhysicsProcessor:
    def process(self, vars_obj, platforms, game_map=None):
        # 1. Y축 좌표를 업데이트하기 전에 '이전 발끝 위치'를 먼저 기록해둡니다.
        old_bottom = vars_obj.y + vars_obj.height

        # 중력 적용 및 실제 Y축 이동
        vars_obj.vertical_velocity += vars_obj.gravity
        vars_obj.y += vars_obj.vertical_velocity

        player_rect = pygame.Rect(vars_obj.x, vars_obj.y, vars_obj.width, vars_obj.height)
        on_sub_platform = False

        # 플랫폼 충돌 검사
        for platform in platforms:
            # [GHOST 분기] 통과형 플랫폼은 물리 판정을 아예 건너뜁니다.
            if not platform.vars.is_solid:
                continue
                
            plat_rect = pygame.Rect(platform.vars.x, platform.vars.y, platform.vars.width, platform.vars.height)
            
            if player_rect.colliderect(plat_rect):
                # ─── A. 떨어지는 중일 때 (착지 처리: SOLID & ONE_WAY 공통) ───
                if vars_obj.vertical_velocity > 0:
                    # 이동하기 전 발끝(old_bottom)이 플랫폼 윗면보다 높게 있었을 때만 착지시킵니다.
                    if old_bottom <= platform.vars.y + 10:
                        vars_obj.y = platform.vars.y - vars_obj.height
                        vars_obj.vertical_velocity = 0
                        vars_obj.is_jumping = False
                        on_sub_platform = True
                        break
                
                # ─── B. 점프하며 올라가는 중일 때 (머리 충돌 처리: ONLY SOLID) ───
                elif vars_obj.vertical_velocity < 0:
                    # 아래에서 위로 통과 불가능한(SOLID) 플랫폼인 경우만 머리를 막습니다.
                    if not platform.vars.passable_from_bottom:
                        # 이동하기 전 정수리가 플랫폼 아랫면보다 아래에 있었는지 검증
                        old_top = vars_obj.y - vars_obj.vertical_velocity
                        if old_top >= platform.vars.y + platform.vars.height:
                            vars_obj.y = platform.vars.y + platform.vars.height
                            vars_obj.vertical_velocity = 0 # 상승 속도 리셋 (뚝 떨어지게 만듦)

        # 메인 바닥 착지 검사
        if not on_sub_platform:
            g_y = game_map.ground_y if (game_map and hasattr(game_map, 'ground_y')) else GROUND_Y
            if vars_obj.y + vars_obj.height >= g_y:
                vars_obj.y = g_y - vars_obj.height
                vars_obj.vertical_velocity = 0
                vars_obj.is_jumping = False

        # 좌측 맵 바운더리 제한
        if vars_obj.x < 0:
            vars_obj.x = 0

        # 우측 맵 바운더리 제한
        max_width = game_map.width if game_map else SCREEN_WIDTH
        if vars_obj.x > max_width - vars_obj.width:
            vars_obj.x = max_width - vars_obj.width