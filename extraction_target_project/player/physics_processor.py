# src/player/physics_processor.py
import pygame
from settings import SCREEN_WIDTH, GROUND_Y

class PlayerPhysicsProcessor:
    def process(self, vars_obj, platforms, game_map=None):
        # 중력 적용 및 이동
        vars_obj.vertical_velocity += vars_obj.gravity
        vars_obj.y += vars_obj.vertical_velocity

        player_rect = pygame.Rect(vars_obj.x, vars_obj.y, vars_obj.width, vars_obj.height)
        on_sub_platform = False

        # 플랫폼 충돌 검사
        for platform in platforms:
            if not platform.vars.is_solid:
                continue
            plat_rect = pygame.Rect(platform.vars.x, platform.vars.y, platform.vars.width, platform.vars.height)
            if player_rect.colliderect(plat_rect):
                if vars_obj.vertical_velocity > 0:
                    if (vars_obj.y + vars_obj.height - vars_obj.vertical_velocity) <= platform.vars.y + 10:
                        vars_obj.y = platform.vars.y - vars_obj.height
                        vars_obj.vertical_velocity = 0
                        vars_obj.is_jumping = False
                        on_sub_platform = True
                        break

        # 메인 바닥 착지 검사
        if not on_sub_platform:
            g_y = game_map.ground_y if (game_map and hasattr(game_map, 'ground_y')) else GROUND_Y
            if vars_obj.y + vars_obj.height >= g_y:
                vars_obj.y = g_y - vars_obj.height
                vars_obj.vertical_velocity = 0
                vars_obj.is_jumping = False

        # ⬅️ 좌측 맵 바운더리 제한 보강
        if vars_obj.x < 0:
            vars_obj.x = 0

        # ➡️ 우측 맵 바운더리 제한 (실시간 맵 크기 반영)
        max_width = game_map.width if game_map else SCREEN_WIDTH
        if vars_obj.x > max_width - vars_obj.width:
            vars_obj.x = max_width - vars_obj.width